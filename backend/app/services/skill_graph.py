"""
Skill Graph Engine (spec sections 5, 24).

Builds a directed prerequisite graph over the full skill catalog using
networkx, resolves a target role into its full skill hierarchy (including
transitive prerequisites, so e.g. requesting "RAG" pulls in embeddings ->
vector search -> transformers automatically), and merges in the learner's
current proficiency to produce the node/edge structure the frontend renders
as the interactive Skill Graph (spec section 45).
"""
from __future__ import annotations

import networkx as nx
from sqlalchemy.orm import Session

from app.data.seed_data import ROLE_SKILLS
from app.models import models as m
from app.services.util import status_for_confidence


def build_full_graph(db: Session) -> nx.DiGraph:
    """Builds a directed graph where edge u->v means `u REQUIRES v`
    (v must be learned first)."""
    g = nx.DiGraph()
    skills = db.query(m.Skill).all()
    for s in skills:
        g.add_node(s.key, id=s.id, name=s.name, category=s.category)

    rels = db.query(m.SkillRelationship).filter(m.SkillRelationship.relation_type == "REQUIRES").all()
    id_to_key = {s.id: s.key for s in skills}
    for r in rels:
        from_key = id_to_key.get(r.from_skill_id)
        to_key = id_to_key.get(r.to_skill_id)
        if from_key and to_key:
            g.add_edge(from_key, to_key, relation_type="REQUIRES")
    return g


def resolve_target_skill_set(db: Session, target_role: str) -> list[str]:
    """Returns the full set of skill keys required for a role, including
    transitive prerequisites of the role's core capabilities, so the graph
    is always internally consistent (spec section 7: prerequisite-aware)."""
    graph = build_full_graph(db)
    core = ROLE_SKILLS.get(target_role, ROLE_SKILLS["AI Engineer"])
    full: set[str] = set()
    for skill_key in core:
        if skill_key not in graph:
            continue
        full.add(skill_key)
        full.update(nx.descendants(graph, skill_key))  # everything it (transitively) requires
    return list(full)


def topological_learning_order(db: Session, skill_keys: list[str]) -> list[str]:
    """Returns skill_keys ordered so prerequisites always come before
    dependents (spec section 24: 'use graph traversal to determine
    learning order')."""
    graph = build_full_graph(db)
    sub = graph.subgraph(skill_keys).copy()
    # nx topo sort on u->REQUIRES->v means v (prereq) should be learned first,
    # so we reverse the edges for the ordering.
    reversed_sub = sub.reverse(copy=True)
    try:
        order = list(nx.topological_sort(reversed_sub))
    except nx.NetworkXUnfeasible:
        order = sorted(skill_keys)  # cyclic fallback, shouldn't happen with curated data
    return order


def get_prerequisites(db: Session, skill_key: str) -> list[str]:
    graph = build_full_graph(db)
    if skill_key not in graph:
        return []
    return list(graph.successors(skill_key))  # direct REQUIRES targets


def get_dependents(db: Session, skill_key: str) -> list[str]:
    graph = build_full_graph(db)
    if skill_key not in graph:
        return []
    return list(graph.predecessors(skill_key))


def learner_skill_map(db: Session, profile_id: str) -> dict[str, m.LearnerSkill]:
    rows = db.query(m.LearnerSkill).filter(m.LearnerSkill.profile_id == profile_id).all()
    skill_ids = {s.id: s.key for s in db.query(m.Skill).all()}
    return {skill_ids[row.skill_id]: row for row in rows if row.skill_id in skill_ids}


def get_or_create_learner_skill(db: Session, profile_id: str, skill_key: str) -> m.LearnerSkill:
    skill = db.query(m.Skill).filter(m.Skill.key == skill_key).first()
    if not skill:
        raise ValueError(f"Unknown skill: {skill_key}")
    row = (
        db.query(m.LearnerSkill)
        .filter(m.LearnerSkill.profile_id == profile_id, m.LearnerSkill.skill_id == skill.id)
        .first()
    )
    if row:
        return row
    row = m.LearnerSkill(profile_id=profile_id, skill_id=skill.id, confidence=0.0, status="unknown", evidence=[])
    db.add(row)
    db.flush()
    return row


def build_skill_graph_out(db: Session, profile_id: str, target_role: str):
    """Assembles the full node/edge payload the frontend renders."""
    from app.schemas.schemas import SkillEdgeOut, SkillGraphOut, SkillNodeOut

    target_keys = resolve_target_skill_set(db, target_role)
    graph = build_full_graph(db)
    learner_skills = learner_skill_map(db, profile_id)
    skills_by_key = {s.key: s for s in db.query(m.Skill).all()}

    nodes = []
    for key in target_keys:
        skill = skills_by_key.get(key)
        if not skill:
            continue
        ls = learner_skills.get(key)
        confidence = ls.confidence if ls else 0.0
        status = ls.status if ls else "unknown"
        evidence = ls.evidence if ls else []
        nodes.append(
            SkillNodeOut(
                id=skill.id,
                key=skill.key,
                name=skill.name,
                category=skill.category,
                confidence=confidence,
                status=status,
                evidence=evidence,
                is_target=True,
            )
        )

    edges = []
    for u, v, data in graph.edges(data=True):
        if u in target_keys and v in target_keys:
            edges.append(SkillEdgeOut(source=u, target=v, relation_type=data.get("relation_type", "REQUIRES")))

    return SkillGraphOut(nodes=nodes, edges=edges)

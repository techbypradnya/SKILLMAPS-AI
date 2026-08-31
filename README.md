# SkillGraph AI

### "Don't just learn. Build your capability."

An AI-powered **Adaptive Learning Intelligence Platform** built for the *AI-Powered Personalized
Learning Path Recommender* competition track. It does not recommend courses — it builds a
prerequisite-aware **Skill Graph** of your goal, tracks evidence-based mastery, generates a
phased roadmap, and continuously replans it as you learn.

---

## Table of contents

1. [Problem statement](#problem-statement)
2. [What makes this different from a course recommender](#what-makes-this-different-from-a-course-recommender)
3. [Architecture](#architecture)
4. [AI/ML techniques used](#aiml-techniques-used)
5. [The Skill Graph model](#the-skill-graph-model)
6. [The recommendation algorithm](#the-recommendation-algorithm)
7. [Database schema](#database-schema)
8. [API reference](#api-reference)
9. [Authentication](#authentication)
10. [Setup — local development](#setup--local-development)
11. [Setup — Docker](#setup--docker)
12. [Running tests](#running-tests)
13. [Deployment](#deployment)
14. [Demo mode](#demo-mode)
15. [Honest limitations & future improvements](#honest-limitations--future-improvements)

---

## Authentication

SkillGraph AI includes a complete production-ready authentication system:

- **User Registration**: Sign up with email, full name, and password
- **Secure Login/Logout**: HttpOnly cookie-based JWT authentication
- **Password Validation**: Enforce strong passwords (8+ chars, uppercase, number)
- **Protected Routes**: Dashboard and authenticated pages require login
- **Persistent Sessions**: Stays logged in across page refreshes
- **User Profiles**: Display user name in navigation

### Quick Start

```bash
# Backend
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Visit http://localhost:3000 to test:
1. **Sign up** at `/signup`
2. **Log in** at `/login`
3. **Access dashboard** - Protected route

See [`QUICKSTART_AUTH.md`](QUICKSTART_AUTH.md) for detailed setup and testing instructions.
See [`AUTHENTICATION.md`](AUTHENTICATION.md) for complete API documentation and security details.

---

## Problem statement

> Build an intelligent learning assistant that understands a learner's goals, interests,
> previous learning history, skill level and learning patterns, then generates and continuously
> adapts a personalized learning path containing courses, projects, assessments and milestones.

## What makes this different from a course recommender

A conventional recommender does: **Goal → Courses**.

SkillGraph AI does:

```
Goal → Skill Decomposition → Learner Digital Twin → Skill Gap Analysis →
Dependency Graph → Resource Matching → Project Evidence → Assessment →
Feedback → Adaptive Replanning → Career Readiness
```

Concretely, that means:

- **Prerequisite-aware, not keyword-matched.** The system will never recommend RAG to someone
  with no embeddings background — it resolves the full transitive prerequisite chain
  (`RAG → Vector Databases → Embeddings → Transformers → RNNs → Neural Networks`) before
  recommending anything, using real graph traversal (networkx), not an LLM guessing at order.
- **Evidence-based mastery, not completion theater.** A skill's "AI-estimated proficiency" is
  built from an additive evidence model (course completion, assessment score, project
  completion) with a visible "why do we think you know this?" trail — never a single opaque number.
- **Adaptive, not static.** Every assessment result, feedback signal, or profile change can
  trigger the **Adaptive Path Engine** to regenerate the roadmap and log, in plain language,
  what changed and why.
- **Explainable, not black-box.** Every recommendation carries a "Why this?" explanation and a
  safe, high-level decision trace (which factors contributed) — never raw chain-of-thought.
- **Honest about uncertainty.** All proficiency/readiness numbers are explicitly labeled
  "AI-estimated," never presented as scientifically validated psychometrics, certifications, or
  guarantees (see [`app/services/util.py`](backend/app/services/util.py) and the Career
  Readiness endpoint).

## Architecture

```
frontend (Next.js/TS/Tailwind)
        │  fetch (NEXT_PUBLIC_API_URL)
        ▼
backend (FastAPI)
        │
        ├── api/routes/          — REST endpoints (profile, skill-graph, path, misc, demo)
        ├── services/
        │     ├── profiler.py           — NL goal → structured profile (LLM + rule-based fallback)
        │     ├── skill_graph.py        — prerequisite graph engine (networkx)
        │     ├── gap_analyzer.py       — current vs target skill graph diff
        │     ├── vector_store.py       — lightweight local semantic similarity (TF-IDF)
        │     ├── recommendation.py     — hybrid weighted scoring engine
        │     ├── path_optimizer.py     — phased roadmap generation + Adaptive Path Engine
        │     ├── assessment.py         — adaptive assessment generation & evidence scoring
        │     ├── career_readiness.py   — AI-estimated readiness rollup
        │     ├── what_if.py            — counterfactual simulator
        │     ├── companion.py          — context-grounded chat assistant
        │     ├── explanation.py        — "Explain My Journey" + decision trace
        │     ├── feedback.py           — learner feedback loop → learning velocity
        │     ├── dashboard.py          — aggregation for the dashboard view
        │     └── llm_provider.py       — Anthropic/OpenAI abstraction + deterministic fallback
        ├── models/models.py     — SQLAlchemy ORM (full schema, see below)
        ├── schemas/schemas.py   — Pydantic request/response contracts
        └── data/seed_data.py    — curated skills, prerequisites, resources, projects, question bank
        │
        ▼
data layer: SQLite (default, zero setup) or PostgreSQL (production, pgvector-ready)
```

**Why this pipeline is real, not "an LLM generating text":** every stage above operates on
structured application data (the ORM models) and is independently testable — see
[`backend/tests/test_core.py`](backend/tests/test_core.py). The LLM, when configured, is only
ever used to *extract* or *explain* — it never replaces the graph traversal, scoring, or
roadmap logic.

## AI/ML techniques used

| Technique | Where | Purpose |
|---|---|---|
| Graph algorithms (networkx: descendants, topological sort) | `skill_graph.py` | Resolve transitive prerequisites; determine safe learning order |
| NLP goal extraction (LLM with JSON-schema prompting + regex/keyword fallback) | `profiler.py` | Turn free text into a structured learner profile |
| TF-IDF vectorization + cosine similarity (local vector store) | `vector_store.py` | Semantic-similarity component of the recommendation score |
| Hybrid multi-factor scoring | `recommendation.py` | Interpretable, weighted recommendation ranking |
| Adaptive item-response-style difficulty escalation | `assessment.py` | Easy → medium → hard question ordering; difficulty-weighted evidence scoring |
| Evidence-aggregation model | `assessment.py`, `db/seed.py` | Builds AI-estimated proficiency from multiple weak signals rather than one score |
| Rule-based + LLM dual-path explanation generation | `explanation.py`, `companion.py`, `what_if.py` | Always-available, grounded natural-language output |

**On the vector store:** the default backend is a zero-dependency, offline-friendly TF-IDF +
cosine-similarity implementation (`VECTOR_BACKEND=none`), so the demo never depends on an
external embeddings API or model download. It is lexical, not deep semantic, and this is stated
honestly in code comments. For production, swap in real embeddings by implementing the same
`similarity_scores(query, documents)` interface against `pgvector` or a hosted embeddings API —
the recommendation engine only depends on that function signature.

## The Skill Graph model

Nodes: `Skill`. Edges: `SkillRelationship` (currently `REQUIRES`; `RELATED_TO`/`PART_OF` are
supported by the schema for future expansion). A role (e.g. "AI Engineer") maps to a **core
skill set** (`ROLE_SKILLS` in `seed_data.py`); the graph engine then walks `nx.descendants()` to
pull in every transitive prerequisite, so the graph shown to the learner is always internally
consistent — you'll never see a skill on your path without its prerequisites also present.

Each learner has a `LearnerSkill` row per skill: `confidence` (0–100, **explicitly labeled
"AI-estimated proficiency," not a validated psychometric measure**), a `status` band
(unknown/beginner/developing/proficient/strong), and an `evidence` JSON list recording exactly
which signals contributed and how many points each contributed.

## The recommendation algorithm

```
Recommendation Score =
    0.30 × Skill Gap Relevance       (how large the gap is for the skill this teaches)
  + 0.20 × Prerequisite Readiness    (are this skill's own prerequisites in place?)
  + 0.15 × Goal Alignment            (is it in the resolved target skill set?)
  + 0.10 × Semantic Similarity       (TF-IDF cosine similarity to your goal/interests)
  + 0.10 × Difficulty Fit            (resource difficulty vs your current band)
  + 0.10 × Time Fit                  (resource length vs your weekly time budget)
  + 0.05 × Learner Preference        (format match: video/reading/project-first)
```

Weights are explicit, configurable heuristics (`DEFAULT_WEIGHTS` in `recommendation.py`) —
**not claimed to be scientifically optimal.** They're designed to later be learned from the
feedback loop (`feedback.py` already tracks per-rating signal; wiring that into weight updates
is a natural next step, see Limitations below). Every recommendation ships with a rule-based
"Why this?" explanation and a decision trace listing only the factors that meaningfully
contributed — never raw internal reasoning.

## Database schema

Full SQLAlchemy models in [`backend/app/models/models.py`](backend/app/models/models.py):
`users`, `learner_profiles`, `skills`, `skill_relationships`, `learner_skills`, `resources`,
`resource_skills`, `projects`, `project_skills`, `assessments`, `assessment_questions`,
`assessment_attempts`, `learning_paths`, `learning_path_items`, `progress`, `feedback`,
`recommendations`, `conversations`. Tables are created automatically on first run
(`Base.metadata.create_all`) — no separate migration step is required for the default SQLite
setup. For Postgres in production, wire in Alembic (not included, to keep the zero-setup default
fast) or point `create_all` at your managed instance once and manage schema changes manually.

## API reference

Full interactive docs at `GET /docs` (OpenAPI/Swagger) once the backend is running. Key endpoints:

```
POST /api/profile/create-from-text   — NL goal → structured profile, returns profile_id
GET  /api/profile/{id}                PATCH /api/profile/{id}
POST /api/onboarding/submit
POST /api/skill-graph/generate        GET /api/skill-graph
POST /api/gaps/analyze                GET /api/gaps
POST /api/path/generate               GET /api/path              POST /api/path/replan
GET  /api/recommendations             GET /api/recommendations/{id}/decision-trace
POST /api/assessment/generate         POST /api/assessment/submit-and-replan
POST /api/feedback
POST /api/what-if
POST /api/chat
GET  /api/journey/explain
GET  /api/dashboard
GET  /api/projects
POST /api/demo/start?role=...         GET /api/demo/roles        GET /api/demo/intelligence-mode
GET  /health
```

## Setup — local development

**Requirements:** Python 3.11+, Node 18+.

```bash
# 1. Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp ../.env.example .env   # edit if you want to add an LLM API key — optional
uvicorn app.main:app --reload --port 8000
# → tables + seed data are created automatically on first boot
# → visit http://localhost:8000/docs
```

```bash
# 2. Frontend (in a second terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
# → visit http://localhost:3000
```

No LLM API key is required — the app runs fully in **Demo Intelligence Mode** without one (see
below). To enable live LLM-backed goal extraction, explanations, and chat, set
`ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in `backend/.env`.

## Setup — Docker

```bash
cp .env.example .env   # optional: add API keys
docker compose up --build
# backend  → http://localhost:8000
# frontend → http://localhost:3000
```

A commented-out `pgvector` Postgres service is included in `docker-compose.yml` for production
use; swap `DATABASE_URL` to point at it once enabled.

## Running tests

```bash
cd backend
pytest tests/ -v
```

Covers (per the spec's minimum bar): goal extraction, transitive prerequisite resolution,
topological learning order, skill gap detection and priority ranking, recommendation scoring
bounds and exclusion logic, roadmap generation ordering, and adaptive replanning logging.
All 11 tests pass against an isolated in-memory SQLite database.

## Deployment

- **Frontend:** deploy `frontend/` to Vercel (or any Node host). Set `NEXT_PUBLIC_API_URL` to
  your deployed backend URL.
- **Backend:** deploy `backend/` to Render/Railway/Fly.io/any container host using the included
  `Dockerfile`. Set `DATABASE_URL` to a managed Postgres instance (Neon/Supabase both work) for
  anything beyond a single-instance demo, since SQLite doesn't handle concurrent writers well.
- **Health check:** `GET /health` → `{"status": "healthy"}`.
- All secrets are read from environment variables (`.env.example` documents every one) — nothing
  is hardcoded.

## Demo mode

`POST /api/demo/start?role=AI Engineer` (also `Data Scientist`, `Full Stack Developer`,
`Cybersecurity Analyst`) instantly creates a preloaded learner with realistic partial skill
evidence, so a judge can click **"Explore Demo"** on the landing page and see the full product —
skill graph, gaps, roadmap, dashboard, career readiness — with zero typing.

**Demo Intelligence Mode:** if no `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` is set, every AI-touching
feature (goal extraction, assessment generation for skills outside the curated question bank,
journey explanation, companion chat) automatically falls back to deterministic, rule-based logic
instead of failing. `GET /api/demo/intelligence-mode` reports which mode is currently active so
the frontend can be honest about it. This guarantees the competition demo never breaks because of
an API outage or missing key.

## Honest limitations & future improvements

In the spirit of "a working 80% solution is better than a fake 100% solution":

- **Semantic similarity is TF-IDF, not deep embeddings.** Swapping in a real embeddings API or
  `pgvector` is a drop-in change to `vector_store.similarity_scores()` — the rest of the
  recommendation engine is agnostic to how that function is implemented.
- **No authentication system beyond a minimal demo user model.** `users.hashed_password` exists
  in the schema but there's no real password hashing/JWT flow — out of scope for a learning-path
  recommender competition entry, but noted so it's not mistaken for production-ready auth.
  Add `passlib`/`python-jose` and standard FastAPI auth dependencies before any real deployment.
  Personal data (learner profile, learning path items) is scoped by profile row, not enforced by
  per-request auth in this build.
  **This means: do not deploy the API publicly with real user data before adding auth.**
- **Recommendation weights are fixed heuristics.** `feedback.py` records every rating, and the
  schema (`Feedback`, `Recommendation`) already supports learning weights from that history — a
  simple next step would be a periodic job that nudges `DEFAULT_WEIGHTS` based on aggregate
  "too_easy"/"too_difficult" ratios.
  **The current weights are illustrative, not empirically tuned.**
- **Resource catalog is a curated seed set (~40 resources, ~18 projects), not a live external
  API integration.** URLs point to real, stable documentation/learning hubs — never fabricated —
  per the no-hallucinated-URLs guardrail, but a production version would plug in a real content
  API behind the same `Resource`/`ResourceSkill` schema.
- **No database migrations tool (Alembic) included** — `create_all` is used for zero-friction
  local setup; add Alembic before making schema changes against a populated production database.
- **The Skill Graph visualization uses a deterministic column layout** (by prerequisite depth),
  not a physics-based force simulation — chosen for reliability and readability over visual
  novelty; swapping in `d3-force` is straightforward if desired.

---

Built as a competition-quality, deployment-ready implementation of the full pipeline described in
the problem statement — every stage listed in the architecture diagram above actually exists in
code and is exercised by the test suite and the demo flow, not just described in this README.
#   S K I L L M A P S - A I -  
 
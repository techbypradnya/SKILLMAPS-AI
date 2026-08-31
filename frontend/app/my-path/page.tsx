"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { api, getStoredProfileId } from "@/lib/api";
import SkillGraphViz, { SkillNode, SkillEdge } from "@/components/SkillGraphViz";
import { ConfidenceBar, EmptyState, Spinner, StatusPill } from "@/components/ui";
import { ProtectedRoute } from "@/components/ProtectedRoute";

type Tab = "skill-map" | "roadmap" | "projects" | "assessments";

const TABS: { id: Tab; label: string }[] = [
  { id: "skill-map", label: "Skill Map" },
  { id: "roadmap", label: "Roadmap" },
  { id: "projects", label: "Projects" },
  { id: "assessments", label: "Assessments" },
];

const FEEDBACK_OPTIONS = [
  { value: "good", label: "Good" },
  { value: "too_easy", label: "Too easy" },
  { value: "too_difficult", label: "Too difficult" },
  { value: "already_knew", label: "Already knew" },
  { value: "not_relevant", label: "Not relevant" },
];

const ITEM_ICON: Record<string, string> = { resource: "◆", project: "▲", checkpoint: "●" };
const VALUE_COLOR: Record<string, string> = { high: "#7CE0B8", medium: "#E8A45C", low: "#8A93A6" };

function MyPathInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tabParam = (searchParams.get("tab") as Tab) || "skill-map";
  const [activeTab, setActiveTab] = useState<Tab>(tabParam);

  function switchTab(tab: Tab) {
    setActiveTab(tab);
    router.replace(`/my-path?tab=${tab}`, { scroll: false });
  }

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        <div>
          <p className="text-sm text-capability">Your learning journey</p>
          <h1 className="font-display text-3xl text-ivory">My Path</h1>
        </div>

        {/* Tab bar — negative margin so active border sits flush on the container border */}
        <div className="flex border-b border-ink-softer">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => switchTab(t.id)}
              className={`-mb-px px-4 py-2 text-sm transition-colors ${
                activeTab === t.id
                  ? "border-b-2 border-capability text-capability"
                  : "text-muted hover:text-ivory"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {activeTab === "skill-map" && <SkillMapTab />}
        {activeTab === "roadmap" && <RoadmapTab />}
        {activeTab === "projects" && <ProjectsTab />}
        {activeTab === "assessments" && <AssessmentsTab />}
      </div>
    </ProtectedRoute>
  );
}

export default function MyPathPage() {
  return (
    <Suspense fallback={<div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>}>
      <MyPathInner />
    </Suspense>
  );
}

/* ─── Skill Map ─────────────────────────────────────────────────────────── */
function SkillMapTab() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [graph, setGraph] = useState<{ nodes: SkillNode[]; edges: SkillEdge[] } | null>(null);
  const [selected, setSelected] = useState<SkillNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (!id) { setLoading(false); return; }
    api.getSkillGraph(id)
      .then((g) => { setGraph(g); setSelected(g.nodes[0] || null); })
      .catch(() => setError("Could not load skill graph."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>;
  if (error) return <p className="text-sm text-signal-coral">{error}</p>;
  if (!profileId || !graph) return (
    <EmptyState title="No skill graph yet" body="Build a learning path first." action={<Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">Get started</Link>} />
  );

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
      <SkillGraphViz nodes={graph.nodes} edges={graph.edges} onSelect={setSelected} />
      <div className="card p-5">
        {selected ? (
          <>
            <p className="text-xs uppercase tracking-wide text-muted">{selected.category}</p>
            <h2 className="font-display text-xl text-ivory">{selected.name}</h2>
            <div className="mt-2"><StatusPill status={selected.status} /></div>
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-xs text-muted">
                <span>AI-estimated proficiency</span>
                <span>{Math.round(selected.confidence)}/100</span>
              </div>
              <ConfidenceBar value={selected.confidence} />
            </div>
            <div className="mt-5">
              <p className="text-xs uppercase tracking-wide text-muted">Evidence</p>
              {selected.evidence?.length ? (
                <ul className="mt-2 space-y-1.5 text-sm">
                  {selected.evidence.map((e: any, i: number) => (
                    <li key={i} className="rounded-md bg-ink-soft px-3 py-2 text-ivory">
                      {e.detail} <span className="text-muted">(+{Math.round(e.points)})</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-2 text-sm text-muted">No evidence yet — complete a resource, assessment, or project.</p>
              )}
            </div>
          </>
        ) : (
          <p className="text-sm text-muted">Select a node to see details.</p>
        )}
      </div>
    </div>
  );
}

/* ─── Roadmap ────────────────────────────────────────────────────────────── */
function RoadmapTab() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [path, setPath] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [replanning, setReplanning] = useState(false);

  async function load(id: string) {
    try { setPath(await api.getPath(id)); }
    catch { setError("Could not load roadmap."); }
    finally { setLoading(false); }
  }

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (id) load(id); else setLoading(false);
  }, []);

  async function handleFeedback(itemId: string, rating: string) {
    if (!profileId) return;
    await api.submitFeedback(profileId, itemId, rating).catch(() => null);
    load(profileId);
  }

  async function handleExplain() {
    if (!profileId) return;
    setExplaining(true);
    try {
      const { explanation: text } = await api.explainJourney(profileId);
      setExplanation(text);
    } catch { setExplanation("Could not generate explanation."); }
    finally { setExplaining(false); }
  }

  async function handleReplan() {
    if (!profileId) return;
    setReplanning(true);
    try { await api.replanPath(profileId, "Manual replan requested."); await load(profileId); }
    catch { /* keep existing path */ }
    finally { setReplanning(false); }
  }

  if (loading) return <div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>;
  if (error) return <p className="text-sm text-signal-coral">{error}</p>;
  if (!profileId || !path) return (
    <EmptyState title="No roadmap yet" body="Generate a skill graph first." action={<Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">Get started</Link>} />
  );

  const phases = Array.from(new Set(path.items.map((i: any) => i.phase_title))) as string[];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted">{path.target_role} · v{path.version}</p>
        <div className="flex flex-wrap gap-2">
          <button onClick={handleExplain} disabled={explaining}
            className="rounded-md border border-ink-softer px-4 py-2 text-sm text-muted hover:text-ivory disabled:opacity-50">
            {explaining ? "Thinking…" : "Explain My Journey"}
          </button>
          <button onClick={handleReplan} disabled={replanning}
            className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink disabled:opacity-50">
            {replanning ? "Replanning…" : "Adapt My Path"}
          </button>
        </div>
      </div>

      {explanation && (
        <div className="card border-capability/30 p-6">
          <p className="text-sm leading-relaxed text-ivory">{explanation}</p>
        </div>
      )}

      {path.replanning_log?.length > 0 && (
        <div className="card p-5">
          <p className="text-xs uppercase tracking-wide text-muted">Adaptive Path Engine — recent changes</p>
          <p className="mt-2 text-sm text-ivory">{path.replanning_log[path.replanning_log.length - 1].reason}</p>
        </div>
      )}

      <div className="space-y-10">
        {phases.map((phase) => (
          <div key={phase}>
            <h2 className="font-display text-xl text-ivory">{phase}</h2>
            <div className="mt-3 space-y-2 border-l border-ink-softer pl-5">
              {path.items.filter((i: any) => i.phase_title === phase).map((item: any) => (
                <div key={item.id} className="relative rounded-lg bg-ink-soft p-4">
                  <span className="absolute -left-[27px] top-5 text-capability">{ITEM_ICON[item.item_type] || "◆"}</span>
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0">
                      <p className={`text-sm ${item.status === "done" ? "text-muted line-through" : "text-ivory"}`}>{item.title}</p>
                      {item.why && <p className="mt-1 text-xs text-muted">{item.why}</p>}
                    </div>
                    <span className="shrink-0 text-xs text-muted">{item.estimated_minutes} min</span>
                  </div>
                  {item.status !== "done" && item.item_type !== "checkpoint" && (
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {FEEDBACK_OPTIONS.map((opt) => (
                        <button key={opt.value} onClick={() => handleFeedback(item.id, opt.value)}
                          className="rounded-full border border-ink-softer px-2.5 py-1 text-[11px] text-muted hover:border-capability/50 hover:text-capability">
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── Projects ───────────────────────────────────────────────────────────── */
function ProjectsTab() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (!id) { setLoading(false); return; }
    api.getProjects(id)
      .then(setProjects)
      .catch(() => setError("Could not load projects."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>;
  if (error) return <p className="text-sm text-signal-coral">{error}</p>;
  if (!profileId) return (
    <EmptyState title="No profile yet" body="Build a learning path first." action={<Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">Get started</Link>} />
  );

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted">Every project demonstrates real skills and becomes portfolio evidence toward mastery.</p>
      <div className="grid gap-4 md:grid-cols-2">
        {projects.map((p) => (
          <div key={p.id} className="card flex flex-col p-5">
            <div className="flex items-start justify-between gap-3">
              <p className="font-display text-lg text-ivory">{p.title}</p>
              <span className="shrink-0 text-xs font-medium" style={{ color: VALUE_COLOR[p.portfolio_value] }}>
                {p.portfolio_value} value
              </span>
            </div>
            <p className="mt-2 flex-1 text-sm text-muted">{p.description}</p>
            <p className="mt-3 text-xs text-muted">{p.difficulty} · ~{p.estimated_hours}h</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {p.skills.map((s: string) => (
                <span key={s} className="rounded-full bg-ink-softer px-2 py-0.5 text-[11px] text-muted">{s.replace(/_/g, " ")}</span>
              ))}
            </div>
            <div className="mt-4">
              <div className="mb-1 flex justify-between text-xs text-muted">
                <span>Skill readiness</span><span>{p.readiness_pct}%</span>
              </div>
              <ConfidenceBar value={p.readiness_pct} />
            </div>
          </div>
        ))}
        {projects.length === 0 && <p className="text-sm text-muted">No role-relevant projects found yet.</p>}
      </div>
    </div>
  );
}

/* ─── Assessments ────────────────────────────────────────────────────────── */
function AssessmentsTab() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [skillOptions, setSkillOptions] = useState<{ key: string; name: string; confidence: number }[]>([]);
  const [selectedSkill, setSelectedSkill] = useState("");
  const [assessment, setAssessment] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (!id) { setLoading(false); return; }
    api.getGaps(id)
      .then((g) => {
        const options = [...g.partial, ...g.missing].map((i: any) => ({
          key: i.skill_key, name: i.skill_name, confidence: i.confidence,
        }));
        setSkillOptions(options);
        setSelectedSkill(options[0]?.key || "");
      })
      .catch(() => setError("Could not load skill gaps."))
      .finally(() => setLoading(false));
  }, []);

  async function startAssessment() {
    if (!profileId || !selectedSkill) return;
    setGenerating(true); setResult(null); setAnswers({}); setError(null);
    try { setAssessment(await api.generateAssessment(profileId, selectedSkill)); }
    catch { setError("Could not generate assessment."); }
    finally { setGenerating(false); }
  }

  async function submit() {
    if (!profileId || !assessment) return;
    setSubmitting(true); setError(null);
    try {
      const payload = assessment.questions.map((q: any) => ({ question_id: q.id, chosen_index: answers[q.id] ?? -1 }));
      setResult(await api.submitAssessment(profileId, assessment.id, payload));
    } catch { setError("Could not submit assessment."); }
    finally { setSubmitting(false); }
  }

  if (loading) return <div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>;
  if (!profileId) return (
    <EmptyState title="No profile yet" body="Build a learning path first." action={<Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">Get started</Link>} />
  );

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <p className="text-sm text-muted">Questions escalate from easy to hard. Results update your AI-estimated proficiency and can trigger a roadmap replan.</p>

      {error && <p className="rounded-lg bg-signal-coral/15 px-4 py-3 text-sm text-signal-coral">{error}</p>}

      <div className="card flex flex-wrap items-center gap-3 p-5">
        <select value={selectedSkill} onChange={(e) => setSelectedSkill(e.target.value)}
          className="min-w-0 flex-1 rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory">
          {skillOptions.map((o) => (
            <option key={o.key} value={o.key}>{o.name} — {Math.round(o.confidence)}/100</option>
          ))}
          {skillOptions.length === 0 && <option disabled>No skills available</option>}
        </select>
        <button onClick={startAssessment} disabled={generating || !selectedSkill}
          className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink disabled:opacity-50">
          {generating ? "Generating…" : "Start assessment"}
        </button>
      </div>

      {assessment && !result && (
        <div className="card space-y-6 p-6">
          <p className="font-display text-lg text-ivory">{assessment.title}</p>
          {assessment.questions.map((q: any, idx: number) => (
            <div key={q.id}>
              <p className="text-sm text-ivory">
                {idx + 1}. {q.prompt} <span className="text-xs text-muted">({q.difficulty})</span>
              </p>
              <div className="mt-2 space-y-1.5">
                {q.options.map((opt: string, i: number) => (
                  <label key={i} className="flex cursor-pointer items-center gap-2 rounded-md bg-ink-soft px-3 py-2 text-sm text-ivory hover:bg-ink-softer">
                    <input type="radio" name={q.id} checked={answers[q.id] === i}
                      onChange={() => setAnswers({ ...answers, [q.id]: i })} className="accent-capability" />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <button onClick={submit} disabled={submitting}
            className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink disabled:opacity-50">
            {submitting ? "Scoring…" : "Submit assessment"}
          </button>
        </div>
      )}

      {result && (
        <div className="card space-y-4 p-6">
          <p className="font-display text-xl text-ivory">
            {result.correct}/{result.total} correct — {result.score_pct}%
          </p>
          <div>
            <div className="mb-1 flex justify-between text-xs text-muted">
              <span>Updated AI-estimated proficiency</span>
              <span>{result.updated_confidence}/100 ({result.updated_status})</span>
            </div>
            <ConfidenceBar value={result.updated_confidence} />
          </div>
          {result.weak_concepts?.length > 0 && (
            <div>
              <p className="text-xs uppercase tracking-wide text-muted">Concepts to revisit</p>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {result.weak_concepts.map((c: string) => (
                  <span key={c} className="rounded-full bg-ink-softer px-2 py-0.5 text-xs text-signal-amber">
                    {c.replace(/_/g, " ")}
                  </span>
                ))}
              </div>
            </div>
          )}
          <p className="text-xs text-muted">Your roadmap has been automatically re-evaluated based on this result.</p>
          <button onClick={() => { setAssessment(null); setResult(null); }}
            className="rounded-md border border-ink-softer px-4 py-2 text-sm text-muted hover:text-ivory">
            Take another assessment
          </button>
        </div>
      )}
    </div>
  );
}

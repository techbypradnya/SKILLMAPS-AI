"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, getStoredProfileId } from "@/lib/api";
import { ConfidenceBar, EmptyState, Spinner } from "@/components/ui";

export default function AssessmentPage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [skillOptions, setSkillOptions] = useState<{ key: string; name: string; confidence: number }[]>([]);
  const [selectedSkill, setSelectedSkill] = useState<string>("");
  const [assessment, setAssessment] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (!id) {
      setLoading(false);
      return;
    }
    api.getGaps(id).then((g) => {
      const options = [...g.partial, ...g.missing].map((i: any) => ({ key: i.skill_key, name: i.skill_name, confidence: i.confidence }));
      setSkillOptions(options);
      setSelectedSkill(options[0]?.key || "");
      setLoading(false);
    });
  }, []);

  async function startAssessment() {
    if (!profileId || !selectedSkill) return;
    setGenerating(true);
    setResult(null);
    setAnswers({});
    const a = await api.generateAssessment(profileId, selectedSkill);
    setAssessment(a);
    setGenerating(false);
  }

  async function submit() {
    if (!profileId || !assessment) return;
    setSubmitting(true);
    const payload = assessment.questions.map((q: any) => ({ question_id: q.id, chosen_index: answers[q.id] ?? -1 }));
    const r = await api.submitAssessment(profileId, assessment.id, payload);
    setResult(r);
    setSubmitting(false);
  }

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (!profileId) {
    return (
      <EmptyState
        title="No profile yet"
        body="Build a learning path first, then take adaptive assessments here to generate real evidence of mastery."
        action={
          <Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
            Get started
          </Link>
        }
      />
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <p className="text-sm text-capability">Evidence-based mastery</p>
        <h1 className="font-display text-3xl text-ivory">Adaptive Assessment</h1>
        <p className="mt-2 text-sm text-muted">
          Questions escalate from easy to hard. Your result directly updates your AI-estimated proficiency and can
          trigger a roadmap replan.
        </p>
      </div>

      <div className="card flex flex-wrap items-center gap-3 p-5">
        <select
          value={selectedSkill}
          onChange={(e) => setSelectedSkill(e.target.value)}
          className="flex-1 rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
        >
          {skillOptions.map((o) => (
            <option key={o.key} value={o.key}>
              {o.name} — currently {Math.round(o.confidence)}/100
            </option>
          ))}
        </select>
        <button onClick={startAssessment} disabled={generating} className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
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
                  <label key={i} className="flex cursor-pointer items-center gap-2 rounded-md bg-ink-soft px-3 py-2 text-sm text-ivory">
                    <input
                      type="radio"
                      name={q.id}
                      checked={answers[q.id] === i}
                      onChange={() => setAnswers({ ...answers, [q.id]: i })}
                    />
                    {opt}
                  </label>
                ))}
              </div>
            </div>
          ))}
          <button onClick={submit} disabled={submitting} className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
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
          <Link href="/roadmap" className="inline-block rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
            View updated roadmap →
          </Link>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, getStoredProfileId } from "@/lib/api";
import { EmptyState, Spinner } from "@/components/ui";

export default function ResourcesPage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [recs, setRecs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [traces, setTraces] = useState<Record<string, string[]>>({});

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (!id) {
      setLoading(false);
      return;
    }
    api.getRecommendations(id, 12).then((r) => {
      setRecs(r);
      setLoading(false);
    });
  }, []);

  async function toggleTrace(refId: string) {
    if (!profileId) return;
    if (traces[refId]) {
      const next = { ...traces };
      delete next[refId];
      setTraces(next);
      return;
    }
    const { factors } = await api.getDecisionTrace(profileId, refId);
    setTraces({ ...traces, [refId]: factors });
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
        body="Build a learning path first to see prerequisite-aware resource recommendations."
        action={
          <Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
            Get started
          </Link>
        }
      />
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-capability">Prerequisite-aware</p>
        <h1 className="font-display text-3xl text-ivory">Recommended Resources</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted">
          Ranked by a hybrid score: skill gap relevance, prerequisite readiness, goal alignment, semantic fit,
          difficulty, time fit, and your preferences.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {recs.map((r) => (
          <div key={r.ref_id} className="card p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-display text-lg text-ivory">{r.title}</p>
                <p className="mt-1 text-xs text-muted">
                  {r.difficulty} · {r.estimated_minutes} min
                </p>
              </div>
              <span className="shrink-0 rounded-full bg-ink-softer px-2.5 py-1 text-xs text-capability">
                {(r.score * 100).toFixed(0)}
              </span>
            </div>
            <p className="mt-3 text-sm text-muted">{r.why}</p>
            <div className="mt-3 flex items-center gap-3">
              {r.url && (
                <a href={r.url} target="_blank" rel="noreferrer" className="text-xs text-capability hover:underline">
                  Open resource →
                </a>
              )}
              <button onClick={() => toggleTrace(r.ref_id)} className="text-xs text-muted hover:text-ivory">
                {traces[r.ref_id] ? "Hide reasoning" : "Show reasoning"}
              </button>
            </div>
            {traces[r.ref_id] && (
              <ul className="mt-3 space-y-1 border-t border-ink-softer pt-3 text-xs text-ivory">
                {traces[r.ref_id].map((f) => (
                  <li key={f}>✓ {f}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {recs.length === 0 && <p className="text-sm text-muted">No recommendations right now — you may have mastered everything queued.</p>}
      </div>
    </div>
  );
}

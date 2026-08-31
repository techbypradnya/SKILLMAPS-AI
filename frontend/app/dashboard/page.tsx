"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, getStoredProfileId } from "@/lib/api";
import { ConfidenceBar, EmptyState, Spinner } from "@/components/ui";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function DashboardPage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (!id) { setLoading(false); return; }
    api.getDashboard(id)
      .then(setDashboard)
      .catch(() => setError("Could not load dashboard data."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <ProtectedRoute>
      {loading ? (
        <div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>
      ) : !profileId || !dashboard ? (
        <EmptyState
          title="No learner profile yet"
          body="Start from the landing page by describing your goal, or explore a preloaded demo learner."
          action={
            <Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
              Go to landing page
            </Link>
          }
        />
      ) : (
        <DashboardContent dashboard={dashboard} error={error} />
      )}
    </ProtectedRoute>
  );
}

function DashboardContent({ dashboard, error }: { dashboard: any; error: string | null }) {
  const readiness = dashboard.career_readiness;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm text-capability">{dashboard.target_role}</p>
          <h1 className="font-display text-3xl text-ivory">Your Dashboard</h1>
        </div>
        <Link href="/my-path" className="rounded-md border border-ink-softer px-4 py-2 text-sm text-muted hover:text-ivory">
          View skill map →
        </Link>
      </div>

      {error && (
        <p className="rounded-lg bg-signal-coral/15 px-4 py-3 text-sm text-signal-coral">{error}</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4">
        <StatCard label="Overall progress" value={`${dashboard.overall_progress}%`} />
        <StatCard label="Current phase" value={dashboard.current_phase || "—"} small />
        <StatCard label="Learning velocity" value={`${Math.round(dashboard.learning_velocity * 100)}`} sub="AI-estimated, 0–100" />
        <StatCard label="Career readiness" value={`${readiness.overall}%`} sub="AI-estimated" />
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="card p-6 md:col-span-2">
          <h2 className="font-display text-xl text-ivory">Next Best Action</h2>
          {dashboard.next_best_action ? (
            <div className="mt-4 rounded-lg bg-ink-soft p-4">
              <p className="text-ivory">{dashboard.next_best_action.title}</p>
              <p className="mt-1 text-sm text-muted">{dashboard.next_best_action.why}</p>
              <p className="mt-2 text-xs text-capability">
                {dashboard.next_best_action.estimated_minutes} min · score {(dashboard.next_best_action.score * 100).toFixed(0)}
              </p>
            </div>
          ) : (
            <p className="mt-4 text-sm text-muted">No pending recommendations right now — great work.</p>
          )}

          <h3 className="mt-6 font-display text-lg text-ivory">Today&apos;s Mission</h3>
          <ul className="mt-3 space-y-2">
            {dashboard.today_mission.map((item: any) => (
              <li key={item.id} className="flex items-center justify-between rounded-md bg-ink-soft px-4 py-2.5 text-sm">
                <span className="min-w-0 truncate text-ivory">{item.title}</span>
                <span className="ml-3 shrink-0 text-xs text-muted">{item.estimated_minutes} min</span>
              </li>
            ))}
            {dashboard.today_mission.length === 0 && (
              <p className="text-sm text-muted">Nothing queued — check your full roadmap.</p>
            )}
          </ul>
        </div>

        <div className="card p-6">
          <h2 className="font-display text-xl text-ivory">Career Readiness</h2>
          <p className="mt-1 text-xs text-muted">AI-estimated, based on your current evidence.</p>
          <div className="mt-4 space-y-3">
            {Object.entries(readiness.breakdown as Record<string, number>).map(([k, v]) => (
              <div key={k}>
                <div className="mb-1 flex justify-between text-xs">
                  <span className="text-muted">{k}</span>
                  <span className="text-ivory">{v}%</span>
                </div>
                <ConfidenceBar value={v} />
              </div>
            ))}
          </div>
          {readiness.blockers?.length > 0 && (
            <div className="mt-5">
              <p className="text-xs uppercase tracking-wide text-muted">What&apos;s blocking you</p>
              <ul className="mt-1.5 space-y-1 text-sm text-signal-coral">
                {readiness.blockers.map((b: string) => (
                  <li key={b}>· {b}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <SkillSummaryCard label="Mastered" value={dashboard.skill_summary.mastered} color="#7CE0B8" />
        <SkillSummaryCard label="Developing" value={dashboard.skill_summary.developing} color="#E8A45C" />
        <SkillSummaryCard label="Missing" value={dashboard.skill_summary.missing} color="#E8735C" />
      </div>

      <div className="flex flex-wrap gap-3">
        <Link href="/my-path?tab=roadmap" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
          Open full roadmap
        </Link>
        <Link href="/companion" className="rounded-md border border-ink-softer px-4 py-2 text-sm text-muted hover:text-ivory">
          Ask the AI Companion
        </Link>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, small }: { label: string; value: string; sub?: string; small?: boolean }) {
  return (
    <div className="card p-5">
      <p className="text-xs uppercase tracking-wide text-muted">{label}</p>
      <p className={`mt-1.5 font-display text-ivory ${small ? "text-base" : "text-2xl"}`}>{value}</p>
      {sub && <p className="mt-0.5 text-xs text-muted">{sub}</p>}
    </div>
  );
}

function SkillSummaryCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="card flex items-center justify-between p-5">
      <span className="text-sm text-muted">{label}</span>
      <span className="font-display text-2xl" style={{ color }}>{value}</span>
    </div>
  );
}

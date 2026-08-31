"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { api, getStoredProfileId } from "@/lib/api";
import { EmptyState, Spinner } from "@/components/ui";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import VoiceMentor from "@/components/VoiceMentor";

type Tab = "chat" | "what-if";

const WHATIF_SUGGESTIONS = [
  "What if I skip SQL?",
  "What if I only have 1 hour a day?",
  "What if I skip statistics?",
  "What if I change to Data Scientist?",
];

function CompanionInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const tabParam = (searchParams.get("tab") as Tab) || "chat";
  const [activeTab, setActiveTab] = useState<Tab>(tabParam);

  function switchTab(tab: Tab) {
    setActiveTab(tab);
    router.replace(`/companion?tab=${tab}`, { scroll: false });
  }

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        <div>
          <p className="text-sm text-capability">AI-powered guidance</p>
          <h1 className="font-display text-3xl text-ivory">Companion</h1>
        </div>

        <div className="flex border-b border-ink-softer">
          <button
            onClick={() => switchTab("chat")}
            className={`-mb-px px-4 py-2 text-sm transition-colors ${
              activeTab === "chat"
                ? "border-b-2 border-capability text-capability"
                : "text-muted hover:text-ivory"
            }`}
          >
            Ask AI
          </button>
          <button
            onClick={() => switchTab("what-if")}
            className={`-mb-px px-4 py-2 text-sm transition-colors ${
              activeTab === "what-if"
                ? "border-b-2 border-capability text-capability"
                : "text-muted hover:text-ivory"
            }`}
          >
            What If?
          </button>
        </div>

        {activeTab === "chat" && <VoiceMentor />}
        {activeTab === "what-if" && <WhatIfTab />}
      </div>
    </ProtectedRoute>
  );
}

export default function CompanionPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[40vh] items-center justify-center">
          <Spinner />
        </div>
      }
    >
      <CompanionInner />
    </Suspense>
  );
}

/* ─── What If ────────────────────────────────────────────────────────────── */
function WhatIfTab() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [scenario, setScenario] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<{ scenario: string; result: any }[]>([]);

  useEffect(() => {
    setProfileId(getStoredProfileId());
  }, []);

  async function run(text: string) {
    if (!profileId || !text.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const r = await api.whatIf(profileId, text);
      setResult(r);
      setHistory((h) => [{ scenario: text, result: r }, ...h].slice(0, 5));
    } catch {
      setError("Could not run simulation. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  if (!profileId) {
    return (
      <EmptyState
        title="No profile yet"
        body="Build a learning path first so the simulator has a real roadmap to recalculate against."
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
      <p className="text-sm text-muted">
        Simulate a decision before making it. Recalculates against your real roadmap.
      </p>

      {error && (
        <p className="rounded-lg bg-signal-coral/15 px-4 py-3 text-sm text-signal-coral">{error}</p>
      )}

      <div className="card space-y-3 p-5">
        <textarea
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          rows={2}
          placeholder="e.g. What if I skip SQL?"
          className="w-full resize-none rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory placeholder:text-muted focus:border-capability focus:outline-none"
        />
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => run(scenario)}
            disabled={loading || !scenario.trim()}
            className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink disabled:opacity-50"
          >
            {loading ? "Simulating…" : "Run simulation"}
          </button>
          {WHATIF_SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => { setScenario(s); run(s); }}
              disabled={loading}
              className="rounded-full border border-ink-softer px-3 py-1 text-xs text-muted hover:text-ivory disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {result && (
        <div className="card p-6">
          <p className="text-xs uppercase tracking-wide text-muted">Scenario</p>
          <p className="mt-1 text-ivory">{result.scenario}</p>
          <ul className="mt-4 space-y-2">
            {result.impact_summary.map((line: string, i: number) => (
              <li key={i} className="rounded-md bg-ink-soft px-4 py-2.5 text-sm text-ivory">
                {line}
              </li>
            ))}
          </ul>
          {typeof result.time_saved_minutes === "number" && (
            <p className="mt-3 text-xs text-capability">
              Time saved: {result.time_saved_minutes} minutes
            </p>
          )}
        </div>
      )}

      {history.length > 1 && (
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-wide text-muted">Recent simulations</p>
          {history.slice(1).map((h, i) => (
            <button
              key={i}
              onClick={() => setResult(h.result)}
              className="block w-full rounded-md bg-ink-soft px-4 py-2 text-left text-sm text-muted hover:text-ivory"
            >
              {h.scenario}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, getStoredProfileId } from "@/lib/api";
import { EmptyState } from "@/components/ui";

const SUGGESTIONS = ["What if I skip SQL?", "What if I only have 1 hour a day?", "What if I skip statistics?"];

export default function WhatIfPage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [scenario, setScenario] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<{ scenario: string; result: any }[]>([]);

  useEffect(() => {
    setProfileId(getStoredProfileId());
  }, []);

  async function run(text: string) {
    if (!profileId || !text.trim()) return;
    setLoading(true);
    const r = await api.whatIf(profileId, text);
    setResult(r);
    setHistory((h) => [{ scenario: text, result: r }, ...h].slice(0, 5));
    setLoading(false);
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
      <div>
        <p className="text-sm text-capability">Counterfactual Learning Insight</p>
        <h1 className="font-display text-3xl text-ivory">What If?</h1>
        <p className="mt-2 text-sm text-muted">
          Simulate a decision before making it. This recalculates against your real roadmap, not a guess.
        </p>
      </div>

      <div className="card space-y-3 p-5">
        <textarea
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
          rows={2}
          placeholder="e.g. What if I skip SQL?"
          className="w-full resize-none rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory placeholder:text-muted"
        />
        <div className="flex flex-wrap items-center gap-2">
          <button onClick={() => run(scenario)} disabled={loading} className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
            {loading ? "Simulating…" : "Run simulation"}
          </button>
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => {
                setScenario(s);
                run(s);
              }}
              className="rounded-full border border-ink-softer px-3 py-1 text-xs text-muted hover:text-ivory"
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
            <p className="mt-3 text-xs text-capability">Time saved: {result.time_saved_minutes} minutes</p>
          )}
        </div>
      )}

      {history.length > 1 && (
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-wide text-muted">Recent simulations</p>
          {history.slice(1).map((h, i) => (
            <button key={i} onClick={() => setResult(h.result)} className="block w-full rounded-md bg-ink-soft px-4 py-2 text-left text-sm text-muted hover:text-ivory">
              {h.scenario}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

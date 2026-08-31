"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, setStoredProfileId } from "@/lib/api";

const CONTRAST_ROWS = [
  { generic: "Recommends courses", skillgraph: "Decides WHAT to learn" },
  { generic: "One-size roadmap", skillgraph: "Explains WHY, in what ORDER" },
  { generic: "Course completion = done", skillgraph: "Requires evidence to PROVE mastery" },
  { generic: "Static plan", skillgraph: "Knows WHEN TO CHANGE the plan" },
];

const DEMO_ROLES = ["AI Engineer", "Data Scientist", "Full Stack Developer", "Cybersecurity Analyst"];

export default function LandingPage() {
  const router = useRouter();
  const [goalText, setGoalText] = useState(
    "I want to become a GenAI Engineer in 6 months. I know Python and basic machine learning. I can study 2 hours a day."
  );
  const [loading, setLoading] = useState(false);
  const [demoLoading, setDemoLoading] = useState<string | null>(null);

  async function handleBuildPath() {
    if (!goalText.trim()) return;
    setLoading(true);
    try {
      const { profile_id } = await api.createProfileFromText(goalText);
      setStoredProfileId(profile_id);
      router.push("/onboarding");
    } finally {
      setLoading(false);
    }
  }

  async function handleDemo(role: string) {
    setDemoLoading(role);
    try {
      const { profile_id } = await api.demoStart(role);
      setStoredProfileId(profile_id);
      await api.generateSkillGraph(profile_id, role);
      await api.generatePath(profile_id);
      router.push("/dashboard");
    } finally {
      setDemoLoading(null);
    }
  }

  return (
    <div className="space-y-24">
      <section className="grid items-center gap-14 md:grid-cols-2">
        <div>
          <p className="mb-4 text-sm text-capability">Adaptive Learning Intelligence Platform</p>
          <h1 className="font-display text-4xl leading-[1.1] text-ivory md:text-5xl">
            Don&apos;t just learn.
            <br />
            Build your capability.
          </h1>
          <p className="mt-6 max-w-md text-muted">
            Tell SkillGraph AI your goal in plain language. It builds a prerequisite-aware map of every
            skill standing between you and that goal, then plans, verifies, and continuously replans your
            path — with evidence, not guesswork.
          </p>

          <div className="mt-8 space-y-3">
            <textarea
              value={goalText}
              onChange={(e) => setGoalText(e.target.value)}
              rows={3}
              className="w-full resize-none rounded-lg border border-ink-softer bg-ink-soft px-4 py-3 text-sm text-ivory placeholder:text-muted focus:border-capability"
              placeholder="Describe your goal, current skills, and how much time you have…"
            />
            <button
              onClick={handleBuildPath}
              disabled={loading}
              className="rounded-lg bg-capability px-5 py-2.5 text-sm font-medium text-ink transition hover:bg-capability-dim disabled:opacity-60"
            >
              {loading ? "Analyzing your goal…" : "Build My Learning Path"}
            </button>
          </div>

          <div className="mt-8">
            <p className="mb-2 text-xs uppercase tracking-wide text-muted">Or explore a preloaded demo learner</p>
            <div className="flex flex-wrap gap-2">
              {DEMO_ROLES.map((role) => (
                <button
                  key={role}
                  onClick={() => handleDemo(role)}
                  disabled={demoLoading !== null}
                  className="rounded-md border border-ink-softer px-3 py-1.5 text-xs text-muted transition hover:border-capability/50 hover:text-ivory disabled:opacity-50"
                >
                  {demoLoading === role ? "Loading…" : `Explore Demo: ${role}`}
                </button>
              ))}
            </div>
          </div>
        </div>

        <HeroGraphIllustration />
      </section>

      <section className="card p-8 md:p-10">
        <p className="font-display text-2xl text-ivory">
          Most learning platforms recommend what to learn.
        </p>
        <div className="mt-6 grid gap-3">
          {CONTRAST_ROWS.map((row) => (
            <div key={row.generic} className="grid grid-cols-[1fr_auto_1fr] items-center gap-4 rounded-lg bg-ink-soft px-4 py-3">
              <span className="text-sm text-muted line-through decoration-signal-coral/60">{row.generic}</span>
              <span className="text-xs text-muted">→</span>
              <span className="text-sm text-capability">{row.skillgraph}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function HeroGraphIllustration() {
  const nodes = [
    { x: 40, y: 160, r: 20, label: "Python", status: "#7CE0B8" },
    { x: 160, y: 80, r: 18, label: "NumPy", status: "#7CE0B8" },
    { x: 160, y: 230, r: 18, label: "SQL", status: "#4E9C82" },
    { x: 290, y: 40, r: 18, label: "Stats", status: "#E8A45C" },
    { x: 290, y: 160, r: 20, label: "ML", status: "#E8A45C" },
    { x: 290, y: 280, r: 16, label: "Viz", status: "#3A4256" },
    { x: 420, y: 100, r: 18, label: "Deep Learning", status: "#E8735C" },
    { x: 420, y: 220, r: 18, label: "Embeddings", status: "#3A4256" },
    { x: 540, y: 160, r: 22, label: "RAG", status: "#3A4256" },
  ];
  const edges: [number, number][] = [
    [1, 0], [2, 0], [3, 1], [4, 1], [4, 2], [5, 2], [6, 4], [7, 6], [8, 7],
  ];
  return (
    <div className="card p-6">
      <svg viewBox="0 0 600 320" className="w-full">
        {edges.map(([a, b], i) => (
          <line key={i} x1={nodes[a].x} y1={nodes[a].y} x2={nodes[b].x} y2={nodes[b].y} stroke="#3A4256" strokeWidth={1.5} opacity={0.6} />
        ))}
        {nodes.map((n, i) => (
          <g key={i}>
            <circle cx={n.x} cy={n.y} r={n.r} fill="#171E2E" stroke={n.status} strokeWidth={2.5} />
            <text x={n.x} y={n.y + n.r + 14} textAnchor="middle" fontSize="11" fill="#8A93A6">
              {n.label}
            </text>
          </g>
        ))}
      </svg>
      <p className="mt-2 text-xs text-muted">
        A live version of this graph builds itself around your goal — mastered skills in mint, gaps in amber and coral.
      </p>
    </div>
  );
}

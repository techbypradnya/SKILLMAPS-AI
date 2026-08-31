import Link from "next/link";

const PIPELINE = [
  "Goal",
  "Skill Decomposition",
  "Learner Digital Twin",
  "Skill Gap Analysis",
  "Dependency Graph",
  "Resource Matching",
  "Project Evidence",
  "Assessment",
  "Feedback",
  "Adaptive Replanning",
  "Career Readiness",
];

export default function InnovationPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-10">
      <div>
        <p className="text-sm text-capability">Why SkillGraph AI</p>
        <h1 className="font-display text-4xl text-ivory">
          Most learning platforms recommend what to learn.
        </h1>
        <p className="mt-4 text-muted">
          SkillGraph AI decides <span className="text-ivory">what</span> to learn, <span className="text-ivory">why</span>{" "}
          to learn it, <span className="text-ivory">in what order</span>, <span className="text-ivory">how much</span> to
          learn, <span className="text-ivory">how to prove mastery</span>, and <span className="text-ivory">when to
          change the plan</span>.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="card p-6">
          <p className="text-xs uppercase tracking-wide text-signal-coral">Traditional recommender</p>
          <div className="mt-3 flex items-center gap-2 text-ivory">
            <span>Goal</span>
            <span className="text-muted">→</span>
            <span>Courses</span>
          </div>
          <p className="mt-4 text-sm text-muted">
            A list of popular or matching courses, with no understanding of what you already know, what
            order things must be learned in, or whether you actually retained anything.
          </p>
        </div>
        <div className="card border-capability/30 p-6">
          <p className="text-xs uppercase tracking-wide text-capability">SkillGraph AI</p>
          <div className="mt-3 flex flex-wrap items-center gap-1.5 text-sm text-ivory">
            {PIPELINE.map((step, i) => (
              <span key={step} className="flex items-center gap-1.5">
                {step}
                {i < PIPELINE.length - 1 && <span className="text-muted">→</span>}
              </span>
            ))}
          </div>
          <p className="mt-4 text-sm text-muted">
            A living pipeline: every recommendation is grounded in your real skill graph, gap analysis, and
            evidence — and the plan itself adapts as that evidence changes.
          </p>
        </div>
      </div>

      <div className="card p-6">
        <h2 className="font-display text-xl text-ivory">Three things that make this different</h2>
        <div className="mt-4 space-y-4 text-sm">
          <div>
            <p className="text-ivory">1. Evidence-based mastery, not course-completion theater</p>
            <p className="mt-1 text-muted">
              A skill isn&apos;t &quot;done&quot; because you watched a video. Confidence is built from assessments,
              coding practice, and shipped projects — each with a visible &quot;why do we think you know this?&quot; trail.
            </p>
          </div>
          <div>
            <p className="text-ivory">2. Prerequisite-aware, not keyword-matched</p>
            <p className="mt-1 text-muted">
              Recommending RAG to someone with no embeddings background is a common failure mode of naive
              recommenders. SkillGraph AI resolves the full transitive prerequisite chain before recommending anything.
            </p>
          </div>
          <div>
            <p className="text-ivory">3. Adaptive, not static</p>
            <p className="mt-1 text-muted">
              Every assessment, feedback signal, and profile change can trigger the Adaptive Path Engine to
              reshape the roadmap — and explain exactly what changed and why.
            </p>
          </div>
        </div>
      </div>

      <div className="flex gap-3">
        <Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">
          Try it yourself
        </Link>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, getStoredProfileId } from "@/lib/api";
import { Spinner } from "@/components/ui";

export default function OnboardingPage() {
  const router = useRouter();
  const [profileId, setProfileId] = useState<string | null>(null);
  const [profile, setProfile] = useState<any>(null);
  const [questions, setQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [skipped, setSkipped] = useState<Record<string, boolean>>({});
  const [step, setStep] = useState<"loading" | "confirm" | "diagnostic" | "generating">("loading");

  useEffect(() => {
    const id = getStoredProfileId();
    if (!id) {
      router.push("/");
      return;
    }
    setProfileId(id);
    (async () => {
      const [p, q] = await Promise.all([api.getProfile(id), api.onboardingQuestions()]);
      setProfile(p);
      setQuestions(q.questions);
      setStep("confirm");
    })();
  }, [router]);

  async function saveProfileEdits() {
    if (!profileId || !profile) return;
    await api.updateProfile(profileId, {
      target_role: profile.target_role,
      experience_level: profile.experience_level,
      timeline_weeks: profile.timeline_weeks,
      weekly_hours: profile.weekly_hours,
    });
    setStep("diagnostic");
  }

  async function finishDiagnostic() {
    if (!profileId) return;
    setStep("generating");
    const payload = questions.map((q) => ({ question: q, answer: answers[q], skipped: !!skipped[q] }));
    await api.submitOnboarding(profileId, payload);
    await api.generateSkillGraph(profileId, profile.target_role);
    await api.generatePath(profileId);
    router.push("/dashboard");
  }

  if (step === "loading" || !profile) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Spinner />
      </div>
    );
  }

  if (step === "confirm") {
    return (
      <div className="mx-auto max-w-xl space-y-6">
        <div>
          <p className="text-sm text-capability">Step 1 of 2</p>
          <h1 className="font-display text-3xl text-ivory">Here&apos;s what I understood</h1>
          <p className="mt-2 text-sm text-muted">
            Here&apos;s the structured profile SkillGraph AI extracted from your goal. Edit anything that&apos;s off.
          </p>
        </div>
        <div className="card space-y-4 p-6">
          <Field label="Target role">
            <select
              value={profile.target_role}
              onChange={(e) => setProfile({ ...profile, target_role: e.target.value })}
              className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
            >
              {profile.available_roles?.map((r: string) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Experience level">
            <select
              value={profile.experience_level}
              onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
              className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Timeline (weeks)">
              <input
                type="number"
                value={profile.timeline_weeks}
                onChange={(e) => setProfile({ ...profile, timeline_weeks: Number(e.target.value) })}
                className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
              />
            </Field>
            <Field label="Hours per week">
              <input
                type="number"
                value={profile.weekly_hours}
                onChange={(e) => setProfile({ ...profile, weekly_hours: Number(e.target.value) })}
                className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
              />
            </Field>
          </div>
        </div>
        <button onClick={saveProfileEdits} className="rounded-lg bg-capability px-5 py-2.5 text-sm font-medium text-ink hover:bg-capability-dim">
          Continue to diagnostic
        </button>
      </div>
    );
  }

  if (step === "diagnostic") {
    return (
      <div className="mx-auto max-w-xl space-y-6">
        <div>
          <p className="text-sm text-capability">Step 2 of 2</p>
          <h1 className="font-display text-3xl text-ivory">AI Learning Diagnostic</h1>
          <p className="mt-2 text-sm text-muted">A few optional questions to sharpen your profile. Skip any that don&apos;t apply.</p>
        </div>
        <div className="card space-y-5 p-6">
          {questions.map((q) => (
            <div key={q}>
              <label className="mb-1.5 block text-sm text-ivory">{q}</label>
              <div className="flex gap-2">
                <input
                  disabled={skipped[q]}
                  value={answers[q] || ""}
                  onChange={(e) => setAnswers({ ...answers, [q]: e.target.value })}
                  className="flex-1 rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory disabled:opacity-40"
                  placeholder="Your answer…"
                />
                <button
                  onClick={() => setSkipped({ ...skipped, [q]: !skipped[q] })}
                  className={`shrink-0 rounded-md border px-3 py-1.5 text-xs ${
                    skipped[q] ? "border-capability text-capability" : "border-ink-softer text-muted"
                  }`}
                >
                  Skip
                </button>
              </div>
            </div>
          ))}
        </div>
        <button onClick={finishDiagnostic} className="rounded-lg bg-capability px-5 py-2.5 text-sm font-medium text-ink hover:bg-capability-dim">
          Build my skill graph
        </button>
      </div>
    );
  }

  return (
    <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3">
      <Spinner />
      <p className="text-sm text-muted">Generating your skill graph and roadmap…</p>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 block text-sm text-ivory">{label}</label>
      {children}
    </div>
  );
}

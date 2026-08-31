"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, getStoredProfileId } from "@/lib/api";
import { EmptyState, Spinner } from "@/components/ui";
import { ProtectedRoute } from "@/components/ProtectedRoute";

export default function ProfilePage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    const id = getStoredProfileId();
    setProfileId(id);
    if (!id) { setLoading(false); return; }
    api.getProfile(id)
      .then(setProfile)
      .catch(() => setSaveMsg({ type: "error", text: "Could not load profile." }))
      .finally(() => setLoading(false));
  }, []);

  async function save() {
    if (!profileId || !profile) return;
    setSaving(true); setSaveMsg(null);
    try {
      await api.updateProfile(profileId, {
        target_role: profile.target_role,
        experience_level: profile.experience_level,
        timeline_weeks: profile.timeline_weeks,
        weekly_hours: profile.weekly_hours,
      });
      setSaveMsg({ type: "success", text: "Changes saved." });
    } catch {
      setSaveMsg({ type: "error", text: "Could not save changes." });
    } finally {
      setSaving(false);
    }
  }

  async function regenerate() {
    if (!profileId || !profile) return;
    setSaving(true); setSaveMsg(null);
    try {
      await api.generateSkillGraph(profileId, profile.target_role);
      await api.replanPath(profileId, "Learner updated their profile.");
      setSaveMsg({ type: "success", text: "Skill graph and roadmap regenerated." });
    } catch {
      setSaveMsg({ type: "error", text: "Could not regenerate. Please try again." });
    } finally {
      setSaving(false);
    }
  }

  return (
    <ProtectedRoute>
      {loading ? (
        <div className="flex min-h-[40vh] items-center justify-center"><Spinner /></div>
      ) : !profileId || !profile ? (
        <EmptyState
          title="No profile yet"
          body="Start from the landing page by describing your goal, or explore a preloaded demo learner."
          action={<Link href="/" className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink">Go to landing page</Link>}
        />
      ) : (
        <div className="mx-auto max-w-xl space-y-6">
          <div>
            <p className="text-sm text-capability">Learner Digital Twin</p>
            <h1 className="font-display text-3xl text-ivory">Your Profile</h1>
            <p className="mt-2 text-sm text-muted">A continuously updated model of your goals, skills, and pace.</p>
          </div>

          {saveMsg && (
            <p className={`rounded-lg px-4 py-3 text-sm ${saveMsg.type === "success" ? "bg-capability/15 text-capability" : "bg-signal-coral/15 text-signal-coral"}`}>
              {saveMsg.text}
            </p>
          )}

          <div className="card space-y-4 p-6">
            <div>
              <label className="mb-1.5 block text-sm text-ivory">Original goal</label>
              <p className="rounded-md bg-ink-soft px-3 py-2 text-sm text-muted">{profile.goal_raw_text || "—"}</p>
            </div>
            <div>
              <label className="mb-1.5 block text-sm text-ivory">Target role</label>
              <select
                value={profile.target_role || ""}
                onChange={(e) => setProfile({ ...profile, target_role: e.target.value })}
                className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
              >
                {profile.available_roles?.map((r: string) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1.5 block text-sm text-ivory">Experience level</label>
              <select
                value={profile.experience_level || "beginner"}
                onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
                className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1.5 block text-sm text-ivory">Timeline (weeks)</label>
                <input type="number" min={1}
                  value={profile.timeline_weeks || 0}
                  onChange={(e) => setProfile({ ...profile, timeline_weeks: Number(e.target.value) })}
                  className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
                />
              </div>
              <div>
                <label className="mb-1.5 block text-sm text-ivory">Hours per week</label>
                <input type="number" min={1}
                  value={profile.weekly_hours || 0}
                  onChange={(e) => setProfile({ ...profile, weekly_hours: Number(e.target.value) })}
                  className="w-full rounded-md border border-ink-softer bg-ink-soft px-3 py-2 text-sm text-ivory"
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-2 pt-2">
              <button onClick={save} disabled={saving}
                className="rounded-md border border-ink-softer px-4 py-2 text-sm text-ivory hover:border-capability/50 disabled:opacity-50">
                {saving ? "Saving…" : "Save changes"}
              </button>
              <button onClick={regenerate} disabled={saving}
                className="rounded-md bg-capability px-4 py-2 text-sm font-medium text-ink disabled:opacity-50">
                {saving ? "Updating…" : "Regenerate skill graph & replan"}
              </button>
            </div>
          </div>
        </div>
      )}
    </ProtectedRoute>
  );
}

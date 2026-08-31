const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API error ${res.status} on ${path}: ${text}`);
  }
  return res.json();
}

export const api = {
  // Demo
  demoRoles: () => request<{ roles: { role: string; learner_name: string; goal: string }[] }>("/api/demo/roles"),
  demoStart: (role: string) =>
    request<{ profile_id: string; target_role: string; learner_name: string }>(
      `/api/demo/start?role=${encodeURIComponent(role)}`,
      { method: "POST" }
    ),
  intelligenceMode: () => request<{ mode: string; provider: string }>("/api/demo/intelligence-mode"),

  // Profile / goal
  analyzeGoal: (text: string) => request<any>("/api/goals/analyze", { method: "POST", body: JSON.stringify({ text }) }),
  createProfileFromText: (text: string) =>
    request<{ profile_id: string; extracted: any }>("/api/profile/create-from-text", {
      method: "POST",
      body: JSON.stringify({ text }),
    }),
  getProfile: (profileId: string) => request<any>(`/api/profile/${profileId}`),
  updateProfile: (profileId: string, payload: any) =>
    request<any>(`/api/profile/${profileId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  onboardingQuestions: () => request<{ questions: string[] }>("/api/onboarding/questions"),
  submitOnboarding: (profileId: string, answers: { question: string; answer?: string; skipped: boolean }[]) =>
    request<any>("/api/onboarding/submit", { method: "POST", body: JSON.stringify({ profile_id: profileId, answers }) }),

  // Skill graph / gaps
  generateSkillGraph: (profileId: string, targetRole: string) =>
    request<any>("/api/skill-graph/generate", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId, target_role: targetRole }),
    }),
  getSkillGraph: (profileId: string) => request<any>(`/api/skill-graph?profile_id=${profileId}`),
  getGaps: (profileId: string) => request<any>(`/api/gaps?profile_id=${profileId}`),

  // Path
  generatePath: (profileId: string) =>
    request<any>("/api/path/generate", { method: "POST", body: JSON.stringify({ profile_id: profileId }) }),
  getPath: (profileId: string) => request<any>(`/api/path?profile_id=${profileId}`),
  replanPath: (profileId: string, reason?: string) =>
    request<any>("/api/path/replan", { method: "POST", body: JSON.stringify({ profile_id: profileId, reason }) }),

  // Recommendations
  getRecommendations: (profileId: string, limit = 10) =>
    request<any[]>(`/api/recommendations?profile_id=${profileId}&limit=${limit}`),
  getDecisionTrace: (profileId: string, refId: string) =>
    request<{ factors: string[] }>(`/api/recommendations/${refId}/decision-trace?profile_id=${profileId}`),

  // Assessment
  generateAssessment: (profileId: string, skillKey: string) =>
    request<any>("/api/assessment/generate", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId, skill_key: skillKey }),
    }),
  submitAssessment: (profileId: string, assessmentId: string, answers: { question_id: string; chosen_index: number }[]) =>
    request<any>("/api/assessment/submit-and-replan", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId, assessment_id: assessmentId, answers }),
    }),

  // Feedback
  submitFeedback: (profileId: string, learningPathItemId: string | null, rating: string, confidence?: number) =>
    request<any>("/api/feedback", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId, learning_path_item_id: learningPathItemId, rating, confidence_1_5: confidence }),
    }),

  // What-if
  whatIf: (profileId: string, scenario: string) =>
    request<any>("/api/what-if", { method: "POST", body: JSON.stringify({ profile_id: profileId, scenario }) }),

  // Chat
  chat: (profileId: string, message: string) =>
    request<{ reply: string; used_context: string[] }>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ profile_id: profileId, message }),
    }),

  // Journey / dashboard
  explainJourney: (profileId: string) => request<{ explanation: string }>(`/api/journey/explain?profile_id=${profileId}`),
  getDashboard: (profileId: string) => request<any>(`/api/dashboard?profile_id=${profileId}`),
  getProjects: (profileId: string) => request<any[]>(`/api/projects?profile_id=${profileId}`),
};

export function getStoredProfileId(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("skillgraph_profile_id");
}

export function setStoredProfileId(id: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("skillgraph_profile_id", id);
}

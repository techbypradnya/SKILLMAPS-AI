"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, loading: authLoading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, authLoading, router]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setFieldErrors({});

    // Validation
    const newFieldErrors: typeof fieldErrors = {};
    if (!email.trim()) {
      newFieldErrors.email = "Email is required";
    }
    if (!password) {
      newFieldErrors.password = "Password is required";
    }

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors);
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-ivory border-t-capability" />
          <p className="mt-4 text-muted">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="mb-12 text-center">
          <Link href="/" className="inline-flex items-baseline gap-2">
            <span className="font-display text-2xl font-semibold text-ivory">SkillGraph</span>
            <span className="font-display text-2xl font-semibold text-capability">AI</span>
          </Link>
          <p className="mt-4 text-sm text-muted">Your career. Your path. Your growth.</p>
        </div>

        {/* Card */}
        <div className="card space-y-6 rounded-xl p-8">
          <div>
            <h1 className="font-display text-2xl text-ivory">Welcome back</h1>
            <p className="mt-2 text-sm text-muted">Continue your journey</p>
          </div>

          {/* Error message */}
          {error && (
            <div className="rounded-lg bg-signal-coral/15 p-3 text-sm text-signal-coral">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-ivory mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className={`w-full rounded-lg border px-4 py-3 text-sm bg-ink-soft text-ivory placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-capability/50 ${
                  fieldErrors.email ? "border-signal-coral" : "border-ink-softer"
                }`}
                disabled={loading}
              />
              {fieldErrors.email && (
                <p className="mt-1 text-xs text-signal-coral">{fieldErrors.email}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-ivory mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className={`w-full rounded-lg border px-4 py-3 text-sm bg-ink-soft text-ivory placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-capability/50 ${
                  fieldErrors.password ? "border-signal-coral" : "border-ink-softer"
                }`}
                disabled={loading}
              />
              {fieldErrors.password && (
                <p className="mt-1 text-xs text-signal-coral">{fieldErrors.password}</p>
              )}
            </div>

            {/* Remember me & Forgot password */}
            <div className="flex items-center justify-between pt-2">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  disabled={loading}
                  className="h-4 w-4 rounded border border-ink-softer bg-ink-soft accent-capability"
                />
                <span className="text-sm text-muted">Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-sm text-capability hover:text-capability-dim">
                Forgot password?
              </Link>
            </div>

            {/* Login button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-gradient-to-r from-signal-coral to-signal-amber px-4 py-3 text-sm font-medium text-ink transition disabled:opacity-60 hover:shadow-lg hover:shadow-signal-coral/30"
            >
              {loading ? "Logging in…" : "Login"}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-ink-softer" />
            <span className="text-xs text-muted">OR</span>
            <div className="h-px flex-1 bg-ink-softer" />
          </div>

          {/* Google OAuth (placeholder) */}
          <button
            type="button"
            disabled
            className="w-full rounded-lg border border-ink-softer px-4 py-3 text-sm font-medium text-muted transition hover:border-capability/50 hover:text-ivory disabled:opacity-60"
          >
            Continue with Google (Coming soon)
          </button>

          {/* Sign up link */}
          <p className="text-center text-sm text-muted">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="font-medium text-capability hover:text-capability-dim">
              Create account
            </Link>
          </p>
        </div>

        {/* Footer note */}
        <p className="mt-8 text-center text-xs text-muted">
          By logging in, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}

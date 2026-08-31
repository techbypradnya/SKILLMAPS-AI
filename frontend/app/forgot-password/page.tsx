"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function ForgotPasswordPage() {
  const router = useRouter();
  
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");
  const [fieldError, setFieldError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setFieldError("");

    if (!email.trim()) {
      setFieldError("Email is required");
      return;
    }

    if (!email.includes("@")) {
      setFieldError("Please enter a valid email");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Request failed");
      }

      setSubmitted(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : "An error occurred";
      setError(message);
    } finally {
      setLoading(false);
    }
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
          {!submitted ? (
            <>
              <div>
                <h1 className="font-display text-2xl text-ivory">Reset your password</h1>
                <p className="mt-2 text-sm text-muted">
                  Enter your email address and we&apos;ll send you a link to reset your password.
                </p>
              </div>

              {/* Error message */}
              {error && (
                <div className="rounded-lg bg-signal-coral/15 p-3 text-sm text-signal-coral">
                  {error}
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-ivory mb-2">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className={`w-full rounded-lg border px-4 py-3 text-sm bg-ink-soft text-ivory placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-capability/50 ${
                      fieldError ? "border-signal-coral" : "border-ink-softer"
                    }`}
                    disabled={loading}
                  />
                  {fieldError && (
                    <p className="mt-1 text-xs text-signal-coral">{fieldError}</p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-lg bg-gradient-to-r from-signal-coral to-signal-amber px-4 py-3 text-sm font-medium text-ink transition disabled:opacity-60 hover:shadow-lg hover:shadow-signal-coral/30"
                >
                  {loading ? "Sending…" : "Send Reset Link"}
                </button>
              </form>

              {/* Back to login */}
              <p className="text-center text-sm text-muted">
                Remember your password?{" "}
                <Link href="/login" className="font-medium text-capability hover:text-capability-dim">
                  Log in
                </Link>
              </p>
            </>
          ) : (
            <>
              <div>
                <div className="mb-4 flex justify-center">
                  <div className="rounded-full bg-capability/20 p-3">
                    <svg className="h-6 w-6 text-capability" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
                <h1 className="font-display text-center text-2xl text-ivory">Check your email</h1>
              </div>

              <p className="text-center text-sm text-muted">
                If an account exists with the email address you entered, you will receive a password reset link shortly.
              </p>

              <p className="text-center text-xs text-muted">
                Didn&apos;t receive the email? Check your spam folder or{" "}
                <button
                  onClick={() => setSubmitted(false)}
                  className="font-medium text-capability hover:text-capability-dim"
                >
                  try again
                </button>
              </p>

              {/* Back to login */}
              <Link
                href="/login"
                className="block rounded-lg border border-ink-softer px-4 py-3 text-center text-sm font-medium text-muted transition hover:border-capability/50 hover:text-ivory"
              >
                Back to login
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

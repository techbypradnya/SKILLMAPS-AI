"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth";

export default function SignUpPage() {
  const router = useRouter();
  const { signup, isAuthenticated, loading: authLoading } = useAuth();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    fullName?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, authLoading, router]);

  // Password validation
  const passwordRequirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    number: /\d/.test(password),
  };

  const allRequirementsMet =
    passwordRequirements.length && passwordRequirements.uppercase && passwordRequirements.number;

  async function handleSignUp(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setFieldErrors({});

    // Validation
    const newFieldErrors: typeof fieldErrors = {};
    
    if (!fullName.trim()) {
      newFieldErrors.fullName = "Full name is required";
    }
    
    if (!email.trim()) {
      newFieldErrors.email = "Email is required";
    } else if (!email.includes("@")) {
      newFieldErrors.email = "Please enter a valid email";
    }
    
    if (!password) {
      newFieldErrors.password = "Password is required";
    } else if (!allRequirementsMet) {
      newFieldErrors.password = "Password does not meet requirements";
    }
    
    if (password !== confirmPassword) {
      newFieldErrors.confirmPassword = "Passwords do not match";
    }

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors);
      return;
    }

    setLoading(true);
    try {
      await signup(fullName, email, password);
      router.push("/dashboard");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Sign up failed";
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
            <h1 className="font-display text-2xl text-ivory">Create your Skill Maps</h1>
            <p className="mt-2 text-sm text-muted">Build a learning path that actually fits you</p>
          </div>

          {/* Error message */}
          {error && (
            <div className="rounded-lg bg-signal-coral/15 p-3 text-sm text-signal-coral">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSignUp} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-ivory mb-2">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                className={`w-full rounded-lg border px-4 py-3 text-sm bg-ink-soft text-ivory placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-capability/50 ${
                  fieldErrors.fullName ? "border-signal-coral" : "border-ink-softer"
                }`}
                disabled={loading}
              />
              {fieldErrors.fullName && (
                <p className="mt-1 text-xs text-signal-coral">{fieldErrors.fullName}</p>
              )}
            </div>

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
              
              {/* Password requirements */}
              {password && (
                <div className="mt-3 space-y-1">
                  <p className="text-xs font-medium text-muted">Password must contain:</p>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs">
                      <span className={passwordRequirements.length ? "text-capability" : "text-muted"}>
                        {passwordRequirements.length ? "✓" : "○"}
                      </span>
                      <span className={passwordRequirements.length ? "text-capability" : "text-muted"}>
                        Minimum 8 characters
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={passwordRequirements.uppercase ? "text-capability" : "text-muted"}>
                        {passwordRequirements.uppercase ? "✓" : "○"}
                      </span>
                      <span className={passwordRequirements.uppercase ? "text-capability" : "text-muted"}>
                        One uppercase letter
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={passwordRequirements.number ? "text-capability" : "text-muted"}>
                        {passwordRequirements.number ? "✓" : "○"}
                      </span>
                      <span className={passwordRequirements.number ? "text-capability" : "text-muted"}>
                        One number
                      </span>
                    </div>
                  </div>
                </div>
              )}
              
              {fieldErrors.password && (
                <p className="mt-1 text-xs text-signal-coral">{fieldErrors.password}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-ivory mb-2">Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                className={`w-full rounded-lg border px-4 py-3 text-sm bg-ink-soft text-ivory placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-capability/50 ${
                  fieldErrors.confirmPassword ? "border-signal-coral" : "border-ink-softer"
                }`}
                disabled={loading}
              />
              {fieldErrors.confirmPassword && (
                <p className="mt-1 text-xs text-signal-coral">{fieldErrors.confirmPassword}</p>
              )}
            </div>

            {/* Sign up button */}
            <button
              type="submit"
              disabled={loading || !allRequirementsMet}
              className="w-full rounded-lg bg-gradient-to-r from-signal-coral to-signal-amber px-4 py-3 text-sm font-medium text-ink transition disabled:opacity-60 hover:shadow-lg hover:shadow-signal-coral/30"
            >
              {loading ? "Creating account…" : "Create Account"}
            </button>
          </form>

          {/* Log in link */}
          <p className="text-center text-sm text-muted">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-capability hover:text-capability-dim">
              Log in
            </Link>
          </p>
        </div>

        {/* Footer note */}
        <p className="mt-8 text-center text-xs text-muted">
          By creating an account, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}

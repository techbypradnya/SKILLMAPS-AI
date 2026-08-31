"use client";

import { createContext, useContext, useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const API_TIMEOUT_MS = 10000;

async function fetchWithTimeout(url: string, options: RequestInit = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error("Request timeout. Server may be unavailable. Please try again.");
    }
    throw error;
  }
}

interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (full_name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  getToken: () => string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const USER_KEY = "skillgraph_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Restore from localStorage immediately so the UI doesn't flash logged-out
    const stored = localStorage.getItem(USER_KEY);
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem(USER_KEY);
      }
    }
    // Verify the cookie is still valid against the backend
    verifySession();
  }, []);

  async function verifySession() {
    try {
      const response = await fetchWithTimeout(`${API_BASE}/api/auth/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const userData: User = await response.json();
        setUser(userData);
        localStorage.setItem(USER_KEY, JSON.stringify(userData));
      } else if (response.status === 401) {
        // Explicit 401 = session expired or never existed — clear state
        setUser(null);
        localStorage.removeItem(USER_KEY);
      }
      // Any other non-200 (5xx, network hiccup) — keep existing localStorage state
    } catch {
      // Backend unreachable — keep whatever was in localStorage, don't log out
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    const response = await fetchWithTimeout(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(error.detail || "Login failed");
    }

    const userData: User = await response.json();
    setUser(userData);
    localStorage.setItem(USER_KEY, JSON.stringify(userData));
  }

  async function signup(full_name: string, email: string, password: string) {
    const response = await fetchWithTimeout(`${API_BASE}/api/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name, email, password }),
      credentials: "include",
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Signup failed" }));
      throw new Error(error.detail || "Signup failed");
    }

    // Signup succeeded — log in to get the auth cookie
    await login(email, password);
  }

  async function logout() {
    try {
      await fetchWithTimeout(`${API_BASE}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch {
      // Ignore network errors on logout
    } finally {
      setUser(null);
      localStorage.removeItem(USER_KEY);
    }
  }

  function getToken(): string | null {
    return null; // Cookie-based auth
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, isAuthenticated: !!user, login, signup, logout, getToken }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

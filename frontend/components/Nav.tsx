"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth";

const LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/my-path", label: "My Path" },
  { href: "/explore", label: "Explore" },
  { href: "/companion", label: "Companion" },
  { href: "/profile", label: "Profile" },
];

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isAuthPage = pathname === "/login" || pathname === "/signup" || pathname === "/forgot-password";
  if (isAuthPage) return null;

  function isActive(href: string) {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  }

  async function handleLogout() {
    setMobileOpen(false);
    await logout();
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-40 border-b border-ink-softer/60 bg-ink/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        {/* Logo */}
        <Link href="/" className="flex items-baseline gap-1.5 shrink-0">
          <span className="font-display text-lg font-semibold text-ivory">Skill Maps</span>
          <span className="font-display text-lg font-semibold text-capability">AI</span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-md px-3 py-1.5 text-sm transition-colors ${
                isActive(link.href) ? "bg-ink-softer text-capability" : "text-muted hover:text-ivory"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Desktop auth */}
        <div className="hidden items-center gap-3 md:flex">
          {isAuthenticated && user ? (
            <>
              <span className="text-sm text-muted">
                Hi, <span className="font-medium text-ivory">{user.full_name?.split(" ")[0] || "there"}</span>
              </span>
              <button
                onClick={handleLogout}
                className="rounded-md border border-ink-softer px-3 py-1.5 text-sm text-muted transition-colors hover:border-signal-coral/50 hover:text-signal-coral"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="rounded-md px-3 py-1.5 text-sm text-muted transition-colors hover:text-ivory">
                Login
              </Link>
              <Link href="/signup" className="rounded-md border border-ink-softer px-3 py-1.5 text-sm text-muted transition-colors hover:border-capability/50 hover:text-capability">
                Sign Up
              </Link>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="flex items-center justify-center rounded-md p-2 text-muted hover:text-ivory md:hidden"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
        >
          {mobileOpen ? (
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="4" y1="4" x2="16" y2="16" /><line x1="16" y1="4" x2="4" y2="16" />
            </svg>
          ) : (
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="3" y1="6" x2="17" y2="6" /><line x1="3" y1="10" x2="17" y2="10" /><line x1="3" y1="14" x2="17" y2="14" />
            </svg>
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="border-t border-ink-softer/60 bg-ink/98 px-6 pb-4 md:hidden">
          <nav className="flex flex-col gap-1 pt-3">
            {LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className={`rounded-md px-3 py-2.5 text-sm transition-colors ${
                  isActive(link.href) ? "bg-ink-softer text-capability" : "text-muted hover:text-ivory"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
          <div className="mt-3 flex flex-col gap-2 border-t border-ink-softer/60 pt-3">
            {isAuthenticated && user ? (
              <>
                <p className="px-3 text-sm text-muted">
                  Hi, <span className="font-medium text-ivory">{user.full_name?.split(" ")[0] || "there"}</span>
                </p>
                <button
                  onClick={handleLogout}
                  className="rounded-md border border-ink-softer px-3 py-2.5 text-left text-sm text-muted hover:text-signal-coral"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" onClick={() => setMobileOpen(false)}
                  className="rounded-md px-3 py-2.5 text-sm text-muted hover:text-ivory">
                  Login
                </Link>
                <Link href="/signup" onClick={() => setMobileOpen(false)}
                  className="rounded-md border border-ink-softer px-3 py-2.5 text-sm text-muted hover:text-capability">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

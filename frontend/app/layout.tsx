import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";
import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: "SkillGraph AI — Don't just learn. Build your capability.",
  description:
    "An adaptive learning intelligence platform that turns your goal into a prerequisite-aware skill graph, evidence-based mastery tracking, and a continuously replanned roadmap.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink font-body text-ivory antialiased">
        <AuthProvider>
          <Nav />
          <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}

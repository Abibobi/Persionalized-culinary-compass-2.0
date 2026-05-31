"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { useTheme } from "./ThemeProvider";

export default function Navbar() {
  const { theme, toggle } = useTheme();
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav className="mb-6 flex items-center justify-between gap-4 py-4">
      <Link href="/" className="flex items-center gap-3 group">
        <div className="relative h-10 w-10 rounded-xl bg-gradient-to-br from-accent to-warning flex items-center justify-center shadow-md group-hover:shadow-glow transition-shadow">
          <span className="text-white text-lg font-bold">🧭</span>
        </div>
        <div>
          <p className="text-base font-semibold tracking-tight">Culinary Compass</p>
          <p className="text-xs text-muted">AI Nutrition Assistant</p>
        </div>
      </Link>

      <div className="flex items-center gap-1">
        <Link className="btn-ghost" href="/search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          Search
        </Link>
        <Link className="btn-ghost" href="/meal-plan">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/></svg>
          Meals
        </Link>
        <Link className="btn-ghost" href="/dashboard">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
          Dashboard
        </Link>

        <div className="ml-2 h-5 w-px bg-line" />

        <button
          type="button"
          className="btn-ghost"
          onClick={toggle}
          aria-label="Toggle theme"
        >
          {theme === "dark" ? "☀️" : "🌙"}
        </button>

        {isAuthenticated ? (
          <div className="flex items-center gap-2 ml-1">
            <Link href="/onboarding" className="btn-ghost text-accent font-semibold">
              {user?.username}
            </Link>
            <button
              type="button"
              className="btn-secondary text-xs px-3 py-1.5"
              onClick={logout}
            >
              Logout
            </button>
          </div>
        ) : (
          <Link href="/login" className="btn-primary ml-1 text-xs px-4 py-2">
            Sign in
          </Link>
        )}
      </div>
    </nav>
  );
}

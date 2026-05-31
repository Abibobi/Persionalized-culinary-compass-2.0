"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({ username_or_email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.post("/auth/login/", form);
      login(res.data.access, res.data.refresh, res.data.user);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="fade-up grid min-h-[75vh] place-items-center">
      <div className="card w-full max-w-md overflow-hidden">
        {/* Top accent bar */}
        <div className="h-1 w-full bg-gradient-to-r from-accent via-warning to-accent" />
        <div className="p-8">
          <div className="text-center">
            <div className="mx-auto mb-4 h-14 w-14 rounded-2xl bg-gradient-to-br from-accent to-warning flex items-center justify-center shadow-lg">
              <span className="text-2xl">🧭</span>
            </div>
            <h1 className="text-3xl font-bold">Welcome back</h1>
            <p className="mt-2 text-sm text-muted">Sign in to your culinary dashboard</p>
          </div>

          <form className="mt-8 space-y-5" onSubmit={onSubmit}>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-2">
                Email or username
              </label>
              <input
                className="input"
                placeholder="demo_vegan"
                value={form.username_or_email}
                onChange={(e) => setForm((prev) => ({ ...prev, username_or_email: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-2">
                Password
              </label>
              <input
                className="input"
                type="password"
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                required
              />
            </div>

            {error && (
              <div className="rounded-lg bg-danger-soft p-3 text-sm text-danger" style={{ background: "var(--color-danger-soft)" }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn-primary w-full justify-center"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted">
              New here?{" "}
              <Link className="font-semibold text-accent hover:underline" href="/signup">
                Create an account
              </Link>
            </p>
          </div>

          <div className="mt-4 rounded-lg bg-accent-soft p-3 text-center">
            <p className="text-xs text-muted">
              Demo: <code className="font-mono text-accent">demo_vegan / demo1234!</code>
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}

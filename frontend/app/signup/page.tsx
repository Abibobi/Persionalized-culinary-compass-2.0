"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.post("/auth/signup/", form);
      login(res.data.access, res.data.refresh, res.data.user);
      router.push("/onboarding");
    } catch (err: any) {
      const data = err?.response?.data;
      const msg = data?.detail ?? data?.username?.[0] ?? data?.email?.[0] ?? "Signup failed.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="fade-up grid min-h-[75vh] place-items-center">
      <div className="card w-full max-w-md overflow-hidden">
        <div className="h-1 w-full bg-gradient-to-r from-accent via-warning to-accent" />
        <div className="p-8">
          <div className="text-center">
            <div className="mx-auto mb-4 h-14 w-14 rounded-2xl bg-gradient-to-br from-accent to-warning flex items-center justify-center shadow-lg">
              <span className="text-2xl">✨</span>
            </div>
            <h1 className="text-3xl font-bold">Create your profile</h1>
            <p className="mt-2 text-sm text-muted">Start your personalized nutrition journey</p>
          </div>

          <form className="mt-8 space-y-5" onSubmit={onSubmit}>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-2">
                Username
              </label>
              <input
                className="input"
                placeholder="your_username"
                value={form.username}
                onChange={(e) => setForm((prev) => ({ ...prev, username: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted mb-2">
                Email
              </label>
              <input
                className="input"
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
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
                placeholder="Min 8 characters"
                value={form.password}
                onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
                required
                minLength={8}
              />
            </div>

            {error && (
              <div className="rounded-lg p-3 text-sm text-danger" style={{ background: "var(--color-danger-soft)" }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              className="btn-primary w-full justify-center"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Sign up"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-muted">
            Already have an account?{" "}
            <Link className="font-semibold text-accent hover:underline" href="/login">
              Log in
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}

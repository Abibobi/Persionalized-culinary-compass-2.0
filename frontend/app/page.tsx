import Link from "next/link";

const features = [
  { icon: "🔍", title: "Smart Search", desc: "Handles typos, mixed intent, and messy prompts with hybrid NLP" },
  { icon: "🛡️", title: "Safety Engine", desc: "Blocks allergens and warns about health condition conflicts" },
  { icon: "🎯", title: "Personalized", desc: "Ranks recipes by your diet, goals, and taste preferences" },
  { icon: "📋", title: "Meal Planning", desc: "Auto-generates full-day plans with nutrition tracking" },
];

export default function HomePage() {
  return (
    <main className="fade-up space-y-12">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl p-8 md:p-12" style={{ background: "var(--gradient-hero)" }}>
        <div className="relative z-10 max-w-2xl">
          <div className="badge badge-accent mb-4">PCC 2.0 — AI-Powered</div>
          <h1 className="text-4xl md:text-5xl font-bold leading-tight tracking-tight">
            Personalized<br />Culinary Compass
          </h1>
          <p className="mt-4 text-base text-text-secondary leading-relaxed max-w-lg">
            A safety-aware food assistant that plans meals, tracks nutrition goals, and 
            understands even the messiest prompts. Built with hybrid NLP and personalized ranking.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link className="btn-primary" href="/search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              Start searching
            </Link>
            <Link className="btn-secondary" href="/signup">
              Create account
            </Link>
          </div>
        </div>
        {/* Decorative circles */}
        <div className="absolute -right-20 -top-20 h-80 w-80 rounded-full bg-accent opacity-[0.04]" />
        <div className="absolute -right-10 bottom-0 h-60 w-60 rounded-full bg-warning opacity-[0.06]" />
      </section>

      {/* Feature Grid */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {features.map((feature, idx) => (
          <div
            key={feature.title}
            className={`card p-6 fade-up fade-up-delay-${Math.min(idx, 3)}`}
          >
            <div className="mb-3 text-2xl">{feature.icon}</div>
            <h3 className="text-base font-semibold font-sans">{feature.title}</h3>
            <p className="mt-2 text-sm text-muted leading-relaxed">{feature.desc}</p>
          </div>
        ))}
      </section>

      {/* Tech Stack */}
      <section className="card p-8">
        <h2 className="text-2xl font-semibold">Technical Architecture</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl bg-accent-soft p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-accent">Backend</p>
            <p className="mt-2 text-sm text-text-secondary">Django 5 · DRF · JWT · Celery · PostgreSQL</p>
          </div>
          <div className="rounded-xl bg-info-soft p-4" style={{ background: "var(--color-info-soft)" }}>
            <p className="text-xs font-semibold uppercase tracking-wider text-info">NLP / Search</p>
            <p className="mt-2 text-sm text-text-secondary">spaCy · RapidFuzz · Hybrid ranking · Gemini fallback</p>
          </div>
          <div className="rounded-xl bg-success-soft p-4" style={{ background: "var(--color-success-soft)" }}>
            <p className="text-xs font-semibold uppercase tracking-wider text-success">Frontend</p>
            <p className="mt-2 text-sm text-text-secondary">Next.js 14 · TypeScript · Tailwind · SWR</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="text-center py-8">
        <p className="text-sm text-muted">
          Demo credentials: <code className="text-accent font-mono">demo_vegan / demo1234!</code>
        </p>
      </section>
    </main>
  );
}

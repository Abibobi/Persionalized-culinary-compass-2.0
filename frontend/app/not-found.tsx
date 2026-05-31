import Link from "next/link";

export default function NotFound() {
  return (
    <main className="fade-up grid min-h-[60vh] place-items-center">
      <div className="card p-8 text-center max-w-md">
        <span className="text-5xl mb-4 block">🧭</span>
        <h1 className="text-3xl font-bold">Lost in the kitchen?</h1>
        <p className="mt-3 text-sm text-muted">
          This page doesn&apos;t exist. Let&apos;s get you back on track.
        </p>
        <Link className="btn-primary mt-6 inline-flex" href="/dashboard">
          Go to dashboard
        </Link>
      </div>
    </main>
  );
}

"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useState, useEffect } from "react";
import api from "@/lib/api";
import { useRecipeDetail } from "@/lib/hooks";
import WarningBadge from "@/components/WarningBadge";
import NutritionBar from "@/components/NutritionBar";

export default function RecipeDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const { data } = useRecipeDetail(Number.isNaN(id) ? null : id);
  const [warnings, setWarnings] = useState<Array<{ rule_key: string; severity: string; message: string }>>([]);
  const [saved, setSaved] = useState(false);

  // Fetch safety warnings for this recipe
  useEffect(() => {
    if (!id || Number.isNaN(id)) return;
    api.get(`/warnings/check/${id}/`)
      .then((res) => setWarnings(res.data))
      .catch(() => {});
  }, [id]);

  const handleSave = async () => {
    try {
      await api.post(`/recipes/${id}/save/`);
      setSaved(true);
    } catch { /* ignore */ }
  };

  const handleFeedback = async (type: "liked" | "disliked") => {
    try {
      await api.post(`/recipes/${id}/feedback/`, { interaction_type: type });
    } catch { /* ignore */ }
  };

  if (!data) {
    return (
      <main className="fade-up">
        <div className="card p-8 text-center">
          <div className="skeleton h-8 w-48 mx-auto mb-4" />
          <div className="skeleton h-4 w-64 mx-auto mb-2" />
          <div className="skeleton h-4 w-32 mx-auto" />
        </div>
      </main>
    );
  }

  const ingredients = data.ingredients.split(",").map((i) => i.trim()).filter(Boolean);
  const vitaminEntries = Object.entries(data.vitamins || {});

  return (
    <main className="fade-up space-y-6">
      {/* Back */}
      <Link href="/search" className="btn-ghost text-xs">
        ← Back to search
      </Link>

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        {/* Main Content */}
        <div className="space-y-6">
          <section className="card overflow-hidden">
            <div className="h-1.5 w-full bg-gradient-to-r from-accent via-warning to-accent" />
            <div className="p-6 md:p-8">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h1 className="text-3xl font-bold">{data.name}</h1>
                  <p className="mt-2 text-sm text-muted leading-relaxed">{data.description}</p>
                </div>
                {data.is_vegetarian && (
                  <span className="badge badge-success flex-shrink-0">🌿 Vegetarian</span>
                )}
              </div>

              {/* Quick Stats */}
              <div className="mt-6 grid grid-cols-4 gap-3">
                {[
                  { label: "Calories", value: `${data.calories}`, unit: "kcal" },
                  { label: "Cook Time", value: `${data.cooking_time}`, unit: "min" },
                  { label: "Spice", value: "🌶️".repeat(data.spicy_level), unit: "" },
                  { label: "Category", value: data.category, unit: "" },
                ].map((stat) => (
                  <div key={stat.label} className="rounded-xl bg-accent-soft p-3 text-center">
                    <p className="text-xs text-muted">{stat.label}</p>
                    <p className="mt-1 text-sm font-bold">{stat.value} {stat.unit}</p>
                  </div>
                ))}
              </div>

              {/* Macros */}
              <div className="mt-6">
                <h2 className="text-lg font-bold mb-3">Macronutrients</h2>
                <div className="grid grid-cols-4 gap-3 mb-3">
                  {[
                    { label: "Protein", value: data.protein, color: "#e85d04" },
                    { label: "Carbs", value: data.carbs, color: "#f59e0b" },
                    { label: "Fat", value: data.fat, color: "#a16207" },
                    { label: "Fiber", value: data.fiber, color: "#059669" },
                  ].map((m) => (
                    <div key={m.label} className="text-center">
                      <p className="text-xl font-bold" style={{ color: m.color }}>{m.value}g</p>
                      <p className="text-xs text-muted">{m.label}</p>
                    </div>
                  ))}
                </div>
                <NutritionBar protein={data.protein} carbs={data.carbs} fat={data.fat} showLabels />
              </div>
            </div>
          </section>

          {/* Ingredients */}
          <section className="card p-6">
            <h2 className="text-xl font-bold mb-4">Ingredients</h2>
            <div className="grid gap-2 sm:grid-cols-2">
              {ingredients.map((ing, idx) => (
                <div key={idx} className="flex items-center gap-2 rounded-lg border border-line px-3 py-2 text-sm">
                  <span className="h-1.5 w-1.5 rounded-full bg-accent flex-shrink-0" />
                  <span className="capitalize">{ing}</span>
                </div>
              ))}
            </div>
          </section>

          {/* Instructions */}
          <section className="card p-6">
            <h2 className="text-xl font-bold mb-4">Instructions</h2>
            <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-line">
              {data.instructions ?? "Detailed instructions coming soon. Check back later!"}
            </p>
          </section>
        </div>

        {/* Sidebar */}
        <aside className="space-y-6">
          {/* Actions */}
          <div className="card p-6 space-y-3">
            <button
              className={`w-full justify-center ${saved ? "btn-secondary" : "btn-primary"}`}
              onClick={handleSave}
              disabled={saved}
            >
              {saved ? "✅ Saved!" : "📌 Save recipe"}
            </button>
            <div className="grid grid-cols-2 gap-2">
              <button className="btn-secondary justify-center text-xs" onClick={() => handleFeedback("liked")}>
                👍 Like
              </button>
              <button className="btn-secondary justify-center text-xs" onClick={() => handleFeedback("disliked")}>
                👎 Dislike
              </button>
            </div>
          </div>

          {/* Safety */}
          <div className="card p-6">
            <h2 className="text-lg font-bold mb-4">🛡️ Safety Check</h2>
            {warnings.length > 0 ? (
              <div className="space-y-3">
                {warnings.map((w, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <WarningBadge severity={w.severity as "info" | "warning" | "danger"} />
                    <p className="text-xs text-muted flex-1">{w.message}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span className="status-dot status-dot-success" />
                <p className="text-xs text-muted">No safety concerns for your profile</p>
              </div>
            )}
          </div>

          {/* Vitamins */}
          {vitaminEntries.length > 0 && (
            <div className="card p-6">
              <h2 className="text-lg font-bold mb-4">Vitamins</h2>
              <div className="space-y-2">
                {vitaminEntries.map(([name, value]) => (
                  <div key={name} className="flex items-center justify-between text-sm">
                    <span className="text-muted capitalize">{name}</span>
                    <span className="font-semibold">{value}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}

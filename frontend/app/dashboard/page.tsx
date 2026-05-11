"use client";

import { useMemo } from "react";
import Link from "next/link";
import api from "@/lib/api";
import { useDashboard, useMealPlan, useProfile, useRecentSearches, useSavedRecipes } from "@/lib/hooks";
import RecipeCard from "@/components/RecipeCard";
import SkeletonCard from "@/components/SkeletonCard";
import WarningBadge from "@/components/WarningBadge";
import NutritionBar from "@/components/NutritionBar";

export default function DashboardPage() {
  const { data: dashboard } = useDashboard();
  const { data: profile } = useProfile();
  const { data: saved, isLoading } = useSavedRecipes();
  const { data: recentSearches } = useRecentSearches();
  const today = new Date().toISOString().split("T")[0];
  const { data: plan, mutate: mutatePlan } = useMealPlan(today);

  const savedRecipes = useMemo(() => saved?.slice(0, 4) ?? [], [saved]);

  const handleGenerate = async () => {
    const res = await api.post("/meal-plans/generate/", {
      date: today,
      num_meals: 4,
      day_type: "normal",
    });
    mutatePlan(res.data, false);
  };

  const mealSlots = ["breakfast", "lunch", "dinner", "snack"] as const;
  const mealIcons = { breakfast: "🌅", lunch: "☀️", dinner: "🌙", snack: "🍿" };

  return (
    <main className="fade-up space-y-6">
      {/* Stats Header */}
      <section className="grid gap-4 sm:grid-cols-3">
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted">Saved Recipes</p>
          <p className="stat-value mt-2">{dashboard?.stats.saved_recipes_count ?? 0}</p>
        </div>
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted">Total Searches</p>
          <p className="stat-value mt-2">{dashboard?.stats.recent_searches_count ?? 0}</p>
        </div>
        <div className="card p-5">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted">Today&apos;s Plan</p>
          <p className="stat-value mt-2">{plan?.total_calories ?? "—"}</p>
          <p className="text-xs text-muted mt-1">kcal planned</p>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        {/* Main Column */}
        <section className="space-y-6">
          {/* Meal Plan Card */}
          <div className="card overflow-hidden">
            <div className="h-1 w-full bg-gradient-to-r from-accent via-warning to-accent" />
            <div className="p-6">
              <div className="flex items-center justify-between mb-5">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted">Today&apos;s Plan</p>
                  <h2 className="mt-1 text-xl font-bold">Active Meal Plan</h2>
                </div>
                <button className="btn-primary text-xs" onClick={handleGenerate} type="button">
                  {plan ? "Regenerate" : "Generate plan"}
                </button>
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {mealSlots.map((meal) => {
                  const item = plan?.items.find((e) => e.meal_type === meal);
                  return (
                    <div key={meal} className="rounded-xl border border-line p-4 hover:border-accent transition-colors">
                      <div className="flex items-center gap-2 mb-2">
                        <span>{mealIcons[meal]}</span>
                        <p className="text-xs font-semibold uppercase tracking-wider text-muted">{meal}</p>
                      </div>
                      <p className="text-sm font-semibold truncate">{item?.recipe_name ?? "Not set"}</p>
                      {item && (
                        <p className="mt-1 text-xs text-muted">
                          {item.calories} kcal · P {item.protein_g}g
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>

              {plan && (
                <div className="mt-5 rounded-xl bg-accent-soft p-4">
                  <div className="flex items-center justify-between text-sm mb-3">
                    <span className="font-semibold">Nutrition Totals</span>
                    <span className="stat-value text-lg">{plan.total_calories} kcal</span>
                  </div>
                  <NutritionBar
                    protein={plan.total_protein_g}
                    carbs={plan.total_carbs_g}
                    fat={plan.total_fat_g}
                    showLabels
                  />
                </div>
              )}
            </div>
          </div>

          {/* Saved Recipes */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">Saved Recipes</h2>
              <Link className="text-xs font-semibold text-accent hover:underline" href="/search">
                Explore more →
              </Link>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {isLoading
                ? Array.from({ length: 4 }).map((_, idx) => <SkeletonCard key={idx} />)
                : savedRecipes.length
                  ? savedRecipes.map((item) => (
                      <RecipeCard key={item.id} recipe={item.recipe} compact />
                    ))
                  : (
                      <div className="sm:col-span-2 text-center py-8">
                        <span className="text-3xl mb-2 block">📚</span>
                        <p className="text-sm text-muted">No saved recipes yet. Start exploring!</p>
                      </div>
                    )}
            </div>
          </div>
        </section>

        {/* Sidebar */}
        <aside className="space-y-6">
          {/* Profile Card */}
          <div className="card p-6">
            <h2 className="text-lg font-bold mb-4">Profile</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted">Diet</span>
                <span className="badge badge-accent capitalize">{profile?.diet_type ?? "—"}</span>
              </div>
              <div className="divider" />
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted">Allergies</span>
                <span className="font-semibold">{profile?.allergies?.length ?? 0}</span>
              </div>
              <div className="divider" />
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted">Cal target</span>
                <span className="font-semibold">{profile?.calorie_target ?? "—"} kcal</span>
              </div>
              <div className="divider" />
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted">Cook time</span>
                <span className="font-semibold">{profile?.max_cooking_time_min ?? "—"} min</span>
              </div>
            </div>
            <Link className="btn-secondary w-full justify-center mt-4 text-xs" href="/onboarding">
              Edit profile
            </Link>
          </div>

          {/* Recent Searches */}
          <div className="card p-6">
            <h2 className="text-lg font-bold mb-4">Recent Searches</h2>
            {recentSearches?.length ? (
              <ul className="space-y-2">
                {recentSearches.slice(0, 5).map((entry) => (
                  <li key={entry.id} className="group rounded-lg border border-line p-3 hover:border-accent transition-colors cursor-pointer">
                    <p className="text-sm font-medium truncate">{entry.raw_query}</p>
                    <div className="mt-1 flex items-center gap-2 text-xs text-muted">
                      <span>{entry.result_count} results</span>
                      <span>·</span>
                      <span>{entry.latency_ms}ms</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted text-center py-4">No searches yet</p>
            )}
          </div>

          {/* Safety Panel */}
          <div className="card p-6">
            <h2 className="text-lg font-bold mb-4">Safety Insights</h2>
            <div className="space-y-2">
              {plan?.warnings?.length ? (
                plan.warnings.map((msg, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <WarningBadge severity="warning" />
                    <p className="text-xs text-muted flex-1">{msg}</p>
                  </div>
                ))
              ) : (
                <div className="flex items-center gap-2">
                  <span className="status-dot status-dot-success" />
                  <p className="text-xs text-muted">No safety flags today</p>
                </div>
              )}
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}

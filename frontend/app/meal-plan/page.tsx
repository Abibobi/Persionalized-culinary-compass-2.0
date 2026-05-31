"use client";

import { useMemo, useState } from "react";
import api from "@/lib/api";
import { useMealPlan } from "@/lib/hooks";
import type { MealPlanItem } from "@/lib/types";
import NutritionBar from "@/components/NutritionBar";
import WarningBadge from "@/components/WarningBadge";

const mealSlots = ["breakfast", "lunch", "dinner", "snack"] as const;
const mealIcons = { breakfast: "🌅", lunch: "☀️", dinner: "🌙", snack: "🍿" };
const dayTypes = [
  { value: "normal", label: "Normal", icon: "🏠" },
  { value: "workout", label: "Workout", icon: "💪" },
  { value: "low_carb", label: "Low Carb", icon: "🥗" },
];

export default function MealPlanPage() {
  const [shopOpen, setShopOpen] = useState(false);
  const [shopping, setShopping] = useState<Array<{ ingredient: string; servings: number }>>([]);
  const [loading, setLoading] = useState(false);
  const [dayType, setDayType] = useState("normal");
  const [numMeals, setNumMeals] = useState<3 | 4>(4);
  const today = new Date().toISOString().split("T")[0];
  const { data: plan, mutate } = useMealPlan(today);

  const itemsByMeal = useMemo(() => {
    const map = new Map<string, MealPlanItem>();
    plan?.items?.forEach((item) => map.set(item.meal_type, item));
    return map;
  }, [plan]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const res = await api.post("/meal-plans/generate/", {
        date: today,
        num_meals: numMeals,
        day_type: dayType,
      });
      mutate(res.data, false);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async (itemId?: number) => {
    if (!plan || !itemId) return;
    try {
      await api.patch(`/meal-plans/${plan.id}/items/${itemId}/regenerate/`);
      mutate();
    } catch { /* ignore */ }
  };

  const handleShopping = async () => {
    if (!plan) {
      setShopOpen(true);
      return;
    }
    const res = await api.get(`/meal-plans/${plan.id}/shopping-list/`);
    setShopping(res.data);
    setShopOpen(true);
  };

  const displaySlots = numMeals === 3
    ? mealSlots.filter((s) => s !== "snack")
    : mealSlots;

  return (
    <main className="fade-up space-y-6">
      {/* Controls */}
      <section className="card overflow-hidden">
        <div className="h-1 w-full bg-gradient-to-r from-accent via-warning to-accent" />
        <div className="p-6 md:p-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold">Daily Meal Plan</h1>
              <p className="mt-1 text-sm text-muted">Auto-generate a full day of meals tailored to your profile.</p>
            </div>
            <button
              className="btn-primary"
              onClick={handleGenerate}
              type="button"
              disabled={loading}
            >
              {loading ? "⏳ Generating..." : plan ? "🔄 Regenerate" : "✨ Generate plan"}
            </button>
          </div>

          {/* Day type & meal count selectors */}
          <div className="mt-6 flex flex-wrap gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">Day Type</p>
              <div className="flex gap-2">
                {dayTypes.map((dt) => (
                  <button
                    key={dt.value}
                    type="button"
                    className={`badge cursor-pointer transition-all ${
                      dayType === dt.value ? "badge-accent shadow-sm" : "bg-surface border border-line"
                    }`}
                    onClick={() => setDayType(dt.value)}
                  >
                    {dt.icon} {dt.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">Meals</p>
              <div className="flex gap-2">
                {[3, 4].map((n) => (
                  <button
                    key={n}
                    type="button"
                    className={`badge cursor-pointer transition-all ${
                      numMeals === n ? "badge-accent shadow-sm" : "bg-surface border border-line"
                    }`}
                    onClick={() => setNumMeals(n as 3 | 4)}
                  >
                    {n} meals
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Meal Cards */}
      <section className="grid gap-4 sm:grid-cols-2">
        {displaySlots.map((slot) => {
          const item = itemsByMeal.get(slot);
          return (
            <div key={slot} className="card p-5 group hover:shadow-lg hover:-translate-y-0.5 transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{mealIcons[slot]}</span>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted">{slot}</p>
                </div>
                {item && (
                  <button
                    className="text-xs text-accent font-semibold hover:underline opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={() => handleRegenerate(item.id)}
                    type="button"
                  >
                    🔄 Swap
                  </button>
                )}
              </div>
              <p className="text-base font-semibold truncate">
                {item?.recipe_name ?? "Not generated yet"}
              </p>
              {item && (
                <>
                  <div className="mt-2 flex gap-3 text-xs text-muted">
                    <span>{item.calories} kcal</span>
                    <span>P {item.protein_g}g</span>
                    <span>C {item.carbs_g}g</span>
                    <span>F {item.fat_g}g</span>
                  </div>
                  <div className="mt-3">
                    <NutritionBar protein={item.protein_g} carbs={item.carbs_g} fat={item.fat_g} />
                  </div>
                </>
              )}
            </div>
          );
        })}
      </section>

      {/* Totals & Actions */}
      <section className="card p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-bold">Nutrition Summary</h2>
            <p className="text-xs text-muted mt-1">
              {plan ? `${plan.total_calories} kcal total · Target: ${plan.target_calories ?? "—"} kcal` : "Generate a plan to see totals"}
            </p>
          </div>
          <button
            type="button"
            className="btn-secondary"
            onClick={handleShopping}
          >
            🛒 Shopping list
          </button>
        </div>
        {plan && (
          <div className="mt-4">
            <NutritionBar
              protein={plan.total_protein_g}
              carbs={plan.total_carbs_g}
              fat={plan.total_fat_g}
              showLabels
            />
          </div>
        )}

        {/* Warnings */}
        {plan?.warnings?.length ? (
          <div className="mt-4 space-y-2">
            {plan.warnings.map((msg, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <WarningBadge severity="warning" />
                <p className="text-xs text-muted">{msg}</p>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      {/* Shopping List Modal */}
      {shopOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[rgba(0,0,0,0.5)] backdrop-blur-sm p-4">
          <div className="card w-full max-w-lg overflow-hidden fade-up">
            <div className="h-1 w-full bg-gradient-to-r from-accent to-warning" />
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold flex items-center gap-2">
                  🛒 Shopping List
                </h3>
                <button className="btn-ghost text-xs" onClick={() => setShopOpen(false)}>
                  ✕ Close
                </button>
              </div>
              {shopping.length ? (
                <ul className="space-y-2 max-h-80 overflow-y-auto">
                  {shopping.map((item) => (
                    <li key={item.ingredient} className="flex items-center justify-between rounded-lg border border-line px-4 py-3 text-sm">
                      <span className="capitalize">{item.ingredient}</span>
                      <span className="badge badge-accent">×{item.servings}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-muted text-center py-8">
                  {plan ? "No ingredients found." : "Generate a meal plan first."}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

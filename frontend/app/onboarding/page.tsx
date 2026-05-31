"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useProfile } from "@/lib/hooks";

const steps = ["Diet & Health", "Preferences", "Nutrition Targets"];
const diets = ["omnivore", "vegetarian", "vegan", "pescatarian", "other"];
const conditions = ["diabetic", "hypertension", "celiac", "heart health", "lactose intolerant"];
const cuisineOptions = ["breakfast", "lunch", "dinner", "snack"];

export default function OnboardingPage() {
  const router = useRouter();
  const { data: profile, mutate } = useProfile();
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [form, setForm] = useState({
    diet_type: "omnivore",
    health_conditions: [] as string[],
    allergies: [] as string[],
    disliked_ingredients: [] as string[],
    preferred_cuisines: [] as string[],
    calorie_target: 2000,
    protein_target_g: 120,
    carbs_target_g: 180,
    fat_target_g: 60,
    max_cooking_time_min: 30,
    spice_tolerance: 3,
    onboarding_completed: true,
  });

  // Initialize form with existing profile data
  useEffect(() => {
    if (profile && !initialized) {
      setForm({
        diet_type: profile.diet_type || "omnivore",
        health_conditions: profile.health_conditions || [],
        allergies: profile.allergies || [],
        disliked_ingredients: profile.disliked_ingredients || [],
        preferred_cuisines: profile.preferred_cuisines || [],
        calorie_target: profile.calorie_target ?? 2000,
        protein_target_g: profile.protein_target_g ?? 120,
        carbs_target_g: profile.carbs_target_g ?? 180,
        fat_target_g: profile.fat_target_g ?? 60,
        max_cooking_time_min: profile.max_cooking_time_min ?? 30,
        spice_tolerance: profile.spice_tolerance ?? 3,
        onboarding_completed: true,
      });
      setInitialized(true);
    }
  }, [profile, initialized]);

  const progress = useMemo(() => ((step + 1) / steps.length) * 100, [step]);

  const updateList = (key: "allergies" | "disliked_ingredients", value: string) => {
    setForm((prev) => ({
      ...prev,
      [key]: value.split(",").map((item) => item.trim()).filter(Boolean),
    }));
  };

  const toggleCondition = (value: string) => {
    setForm((prev) => ({
      ...prev,
      health_conditions: prev.health_conditions.includes(value)
        ? prev.health_conditions.filter((item) => item !== value)
        : [...prev.health_conditions, value],
    }));
  };

  const toggleCuisine = (value: string) => {
    setForm((prev) => ({
      ...prev,
      preferred_cuisines: prev.preferred_cuisines.includes(value)
        ? prev.preferred_cuisines.filter((item) => item !== value)
        : [...prev.preferred_cuisines, value],
    }));
  };

  const submit = async () => {
    setSaving(true);
    try {
      await api.put("/users/me/profile/", form);
      await mutate();
      router.push("/dashboard");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="fade-up mx-auto max-w-3xl">
      <div className="card overflow-hidden">
        <div className="h-1 w-full bg-gradient-to-r from-accent via-warning to-accent" />
        <div className="p-6 md:p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-muted">Onboarding</p>
              <h1 className="mt-1 text-2xl md:text-3xl font-bold">Shape your nutrition compass</h1>
            </div>
            <span className="badge badge-accent">
              {step + 1} / {steps.length}
            </span>
          </div>

          {/* Step Indicators */}
          <div className="mt-4 flex gap-2">
            {steps.map((s, idx) => (
              <button
                key={s}
                type="button"
                onClick={() => setStep(idx)}
                className={`flex-1 rounded-full h-1.5 transition-all ${
                  idx <= step ? "bg-accent" : "bg-line"
                }`}
              />
            ))}
          </div>
          <p className="mt-2 text-xs text-muted">{steps[step]}</p>

          {/* Step 0: Diet & Health */}
          {step === 0 && (
            <section className="mt-8 space-y-8 fade-up">
              <div>
                <p className="text-sm font-semibold mb-3">Diet type</p>
                <div className="flex flex-wrap gap-2">
                  {diets.map((diet) => (
                    <button
                      key={diet}
                      type="button"
                      className={`badge cursor-pointer transition-all capitalize ${
                        form.diet_type === diet ? "badge-accent shadow-sm" : "bg-surface border border-line"
                      }`}
                      onClick={() => setForm((prev) => ({ ...prev, diet_type: diet }))}
                    >
                      {diet}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-sm font-semibold mb-3">Health conditions</p>
                <div className="grid gap-2 sm:grid-cols-2">
                  {conditions.map((condition) => (
                    <label key={condition} className="flex items-center gap-3 rounded-lg border border-line p-3 cursor-pointer hover:border-accent transition-colors">
                      <input
                        type="checkbox"
                        className="h-4 w-4 rounded accent-accent"
                        checked={form.health_conditions.includes(condition)}
                        onChange={() => toggleCondition(condition)}
                      />
                      <span className="text-sm capitalize">{condition}</span>
                    </label>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Step 1: Preferences */}
          {step === 1 && (
            <section className="mt-8 space-y-6 fade-up">
              <div>
                <label className="block text-sm font-semibold mb-2">Allergies</label>
                <input
                  className="input"
                  placeholder="peanuts, soy, shellfish..."
                  defaultValue={form.allergies.join(", ")}
                  onBlur={(e) => updateList("allergies", e.target.value)}
                />
                <p className="mt-1 text-xs text-muted">Comma-separated. These trigger danger-level blocks.</p>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Disliked ingredients</label>
                <input
                  className="input"
                  placeholder="mushrooms, bitter gourd..."
                  defaultValue={form.disliked_ingredients.join(", ")}
                  onBlur={(e) => updateList("disliked_ingredients", e.target.value)}
                />
              </div>
              <div>
                <p className="text-sm font-semibold mb-3">Preferred meal categories</p>
                <div className="flex flex-wrap gap-2">
                  {cuisineOptions.map((c) => (
                    <button
                      key={c}
                      type="button"
                      className={`badge cursor-pointer capitalize transition-all ${
                        form.preferred_cuisines.includes(c) ? "badge-accent shadow-sm" : "bg-surface border border-line"
                      }`}
                      onClick={() => toggleCuisine(c)}
                    >
                      {c}
                    </button>
                  ))}
                </div>
              </div>
            </section>
          )}

          {/* Step 2: Nutrition Targets */}
          {step === 2 && (
            <section className="mt-8 fade-up">
              <div className="grid gap-5 sm:grid-cols-2">
                {[
                  { label: "Calorie target", key: "calorie_target", unit: "kcal" },
                  { label: "Max cook time", key: "max_cooking_time_min", unit: "min" },
                  { label: "Protein target", key: "protein_target_g", unit: "g" },
                  { label: "Carbs target", key: "carbs_target_g", unit: "g" },
                  { label: "Fat target", key: "fat_target_g", unit: "g" },
                ].map(({ label, key, unit }) => (
                  <div key={key}>
                    <label className="block text-sm font-semibold mb-2">{label}</label>
                    <div className="relative">
                      <input
                        className="input pr-12"
                        type="number"
                        value={(form as any)[key] ?? 0}
                        onChange={(e) => setForm((prev) => ({ ...prev, [key]: Number(e.target.value) }))}
                      />
                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted">{unit}</span>
                    </div>
                  </div>
                ))}

                <div className="sm:col-span-2">
                  <label className="block text-sm font-semibold mb-2">
                    Spice tolerance: <span className="text-accent font-bold">{form.spice_tolerance}</span> / 5
                  </label>
                  <input
                    className="w-full accent-accent"
                    type="range"
                    min={1}
                    max={5}
                    value={form.spice_tolerance}
                    onChange={(e) => setForm((prev) => ({ ...prev, spice_tolerance: Number(e.target.value) }))}
                  />
                  <div className="flex justify-between text-xs text-muted mt-1">
                    <span>Mild</span>
                    <span>🔥 Extra Hot</span>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Navigation */}
          <div className="mt-8 flex items-center justify-between">
            <button
              type="button"
              className="btn-secondary"
              disabled={step === 0}
              onClick={() => setStep((prev) => Math.max(prev - 1, 0))}
            >
              ← Back
            </button>
            {step < steps.length - 1 ? (
              <button
                type="button"
                className="btn-primary"
                onClick={() => setStep((prev) => Math.min(prev + 1, steps.length - 1))}
              >
                Next →
              </button>
            ) : (
              <button
                type="button"
                className="btn-primary"
                onClick={submit}
                disabled={saving}
              >
                {saving ? "Saving..." : "✅ Save profile"}
              </button>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

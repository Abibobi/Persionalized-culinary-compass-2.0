"use client";

import { useMemo, useState } from "react";
import api from "@/lib/api";
import { useRankedRecipes } from "@/lib/hooks";
import RecipeCard from "@/components/RecipeCard";
import SkeletonCard from "@/components/SkeletonCard";
import WarningBadge from "@/components/WarningBadge";

const promptSuggestions = [
  "High protein vegetarian dinner",
  "Low calorie breakfast under 30 min",
  "Spicy vegan lunch with lentils",
  "Quick healthy snack with oats",
  "Comforting soup with chickpeas",
];

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState<string | null>(null);
  const {
    data: results,
    aiSuggestions,
    warnings,
    normalizedQuery,
    parsedFilters,
    isLoading,
    mutate,
  } = useRankedRecipes(activeQuery);

  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setActiveQuery(query.trim() || null);
  };

  const onSave = async (id: number) => {
    try {
      await api.post(`/recipes/${id}/save/`);
    } catch { /* ignore */ }
  };

  const onLike = async (id: number) => {
    try {
      await api.post(`/recipes/${id}/feedback/`, { interaction_type: "liked" });
      mutate();
    } catch { /* ignore */ }
  };

  const warningsByRecipe = useMemo(() => {
    const map = new Map<number, Array<{ severity: string; message: string }>>();
    warnings?.forEach((entry) => {
      map.set(
        entry.recipe_id,
        entry.warnings.map((w) => ({
          severity: w.severity ?? "warning",
          message: w.message ?? "",
        }))
      );
    });
    return map;
  }, [warnings]);

  return (
    <main className="fade-up space-y-6">
      {/* Search Box */}
      <section className="card p-6 md:p-8">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-2xl">🔍</span>
          <h1 className="text-2xl md:text-3xl font-bold">Ask me anything about food</h1>
        </div>
        <p className="text-sm text-muted ml-10">
          Try messy prompts, macros, or cravings — I handle typos too.
        </p>

        <form className="mt-5 flex flex-col gap-3 md:flex-row" onSubmit={onSubmit}>
          <input
            className="input flex-1"
            placeholder="e.g., high protien vegetarian dinnr with spinch..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="btn-primary whitespace-nowrap" type="submit">
            Search recipes
          </button>
        </form>

        <div className="mt-4 flex flex-wrap gap-2">
          {promptSuggestions.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="badge badge-accent cursor-pointer hover:shadow-sm transition-shadow"
              onClick={() => {
                setQuery(prompt);
                setActiveQuery(prompt);
              }}
            >
              {prompt}
            </button>
          ))}
        </div>
      </section>

      {/* Query Understanding */}
      {normalizedQuery && activeQuery && (
        <section className="card p-4 fade-up">
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span className="text-muted">Normalized:</span>
            <code className="rounded bg-accent-soft px-2 py-1 text-accent font-mono">
              {normalizedQuery}
            </code>
            {parsedFilters && Object.entries(parsedFilters).map(([key, val]) => (
              <span key={key} className="badge badge-info">
                {key}: {String(val)}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Results Grid */}
      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {isLoading
          ? Array.from({ length: 6 }).map((_, idx) => <SkeletonCard key={idx} />)
          : results?.length
            ? results.map((recipe) => (
                <RecipeCard
                  key={recipe.id}
                  recipe={recipe}
                  explanation={recipe.explanation?.why}
                  onSave={() => onSave(recipe.id)}
                  onLike={() => onLike(recipe.id)}
                />
              ))
            : activeQuery && !isLoading
              ? (
                  <div className="card p-8 md:col-span-2 lg:col-span-3 text-center">
                    <span className="text-4xl mb-3 block">🍽️</span>
                    <h3 className="text-lg font-semibold font-sans">No matches found</h3>
                    <p className="mt-2 text-sm text-muted">
                      Try broadening your query or using different ingredients.
                    </p>
                  </div>
                )
              : !activeQuery
                ? (
                    <div className="card p-8 md:col-span-2 lg:col-span-3 text-center">
                      <span className="text-4xl mb-3 block">💬</span>
                      <h3 className="text-lg font-semibold font-sans">Start with a prompt</h3>
                      <p className="mt-2 text-sm text-muted">
                        Type anything — ingredients, meal types, macros, or cravings.
                      </p>
                    </div>
                  )
                : null}
      </section>

      {/* AI Suggestions fallback */}
      {aiSuggestions && aiSuggestions.recipes?.length > 0 && (
        <section className="card p-6 fade-up">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">🤖</span>
            <h2 className="text-xl font-semibold">AI-Generated Suggestions</h2>
            <WarningBadge severity="info" label="AI" />
          </div>
          <p className="text-xs text-muted mb-4">{aiSuggestions.note}</p>
          <div className="grid gap-4 md:grid-cols-2">
            {aiSuggestions.recipes.map((r, idx) => (
              <div key={idx} className="rounded-xl border border-line p-4">
                <h3 className="font-semibold text-sm">{r.name}</h3>
                <p className="mt-1 text-xs text-muted">{r.description}</p>
                <div className="mt-2 flex gap-3 text-xs text-text-secondary">
                  <span>{r.estimated_calories} kcal</span>
                  <span>P {r.protein_g}g</span>
                  <span>C {r.carbs_g}g</span>
                  <span>F {r.fat_g}g</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Safety Warnings */}
      {warnings?.length > 0 && (
        <section className="card p-6 fade-up">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">🛡️</span>
            <h2 className="text-xl font-semibold">Safety Notes</h2>
          </div>
          <div className="space-y-3">
            {warnings.map((entry) => (
              <div key={entry.recipe_id} className="rounded-xl border border-line p-3">
                <p className="text-xs font-semibold mb-2">Recipe #{entry.recipe_id}</p>
                <div className="space-y-1">
                  {warningsByRecipe.get(entry.recipe_id)?.map((w, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-muted">
                      <WarningBadge severity={w.severity as "warning" | "danger" | "info"} />
                      <span>{w.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

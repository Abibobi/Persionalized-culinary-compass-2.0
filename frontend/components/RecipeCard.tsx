"use client";

import Link from "next/link";
import type { RankedRecipe, RecipeSummary } from "@/lib/types";
import NutritionBar from "./NutritionBar";

type RecipeCardProps = {
  recipe: RankedRecipe | RecipeSummary;
  onSave?: () => void;
  onLike?: () => void;
  explanation?: string;
  compact?: boolean;
};

const mealIcons: Record<string, string> = {
  breakfast: "🌅",
  lunch: "☀️",
  dinner: "🌙",
  snack: "🍿",
};

export default function RecipeCard({ recipe, onSave, onLike, explanation, compact }: RecipeCardProps) {
  const hasScore = "score" in recipe;
  const scorePercent = hasScore ? Math.round((recipe as RankedRecipe).score * 100) : null;

  return (
    <article className="card group flex h-full flex-col overflow-hidden transition-all hover:shadow-lg hover:-translate-y-0.5">
      {/* Header gradient strip */}
      <div className="h-1.5 w-full bg-gradient-to-r from-accent via-warning to-accent opacity-60 group-hover:opacity-100 transition-opacity" />

      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <h3 className="text-base font-semibold truncate">{recipe.name}</h3>
            <div className="mt-1 flex items-center gap-2 text-xs text-muted">
              <span>{mealIcons[recipe.category?.toLowerCase()] ?? "🍽️"}</span>
              <span className="capitalize">{recipe.category}</span>
              <span className="text-line">·</span>
              <span>{recipe.cooking_time} min</span>
              {recipe.is_vegetarian && (
                <>
                  <span className="text-line">·</span>
                  <span className="badge-success badge text-[10px]">Veg</span>
                </>
              )}
            </div>
          </div>
          {scorePercent !== null && (
            <div className="flex-shrink-0">
              <span className="badge badge-accent text-xs font-bold">
                {scorePercent}%
              </span>
            </div>
          )}
        </div>

        {!compact && (
          <>
            <div className="flex items-center justify-between text-xs text-text-secondary">
              <span className="font-semibold">{recipe.calories} kcal</span>
              <span>P {recipe.protein}g · C {recipe.carbs}g · F {recipe.fat}g</span>
            </div>
            <NutritionBar protein={recipe.protein} carbs={recipe.carbs} fat={recipe.fat} />
          </>
        )}

        {explanation && (
          <p className="rounded-lg bg-accent-soft px-3 py-2 text-xs text-accent leading-relaxed">
            💡 {explanation}
          </p>
        )}

        <div className="mt-auto flex items-center justify-between pt-2">
          <Link
            className="text-xs font-semibold text-accent hover:underline underline-offset-2"
            href={`/recipes/${recipe.id}`}
          >
            View details →
          </Link>
          <div className="flex items-center gap-1.5">
            {onSave && (
              <button
                type="button"
                className="btn-secondary text-[11px] px-3 py-1"
                onClick={onSave}
              >
                Save
              </button>
            )}
            {onLike && (
              <button
                type="button"
                className="btn-primary text-[11px] px-3 py-1"
                onClick={onLike}
              >
                ♥ Like
              </button>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}

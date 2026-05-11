from types import SimpleNamespace
from typing import Dict, List, Tuple

from django.db.models import Count
from rapidfuzz import fuzz

from accounts.models import UserRecipeInteraction
from safety.services.rules_engine import filter_dangerous_recipes

from .explanations import ExplanationBuilder
from .ingredients_vocab import INGREDIENT_VOCAB


def score_recipe(recipe):
    """Legacy baseline score used by older callers."""
    protein = recipe.protein or 0
    calories = recipe.calories or 0

    return (protein * 2) - (calories / 100)


def rank_recipes(recipes, parsed_filters=None, user_profile=None, query=None):
    recipes = list(recipes)

    profile = user_profile or _blank_profile()
    query_text = (query or "").strip().lower()
    query_ingredients = _extract_query_ingredients(query_text)

    if user_profile is None:
        safe_pairs = [(recipe, []) for recipe in recipes]
        blocked = []
    else:
        safe_pairs, blocked = filter_dangerous_recipes(recipes, profile)

    popularity_map = _popularity_scores([recipe.id for recipe, _ in safe_pairs])
    explainer = ExplanationBuilder()

    ranked = []
    for recipe, warnings in safe_pairs:
        semantic = _semantic_score(query_text, recipe)
        ingredient_match = _ingredient_match_score(query_text, recipe, query_ingredients)
        profile_fit = _profile_fit_score(profile, recipe)
        nutrition_goal_fit = _nutrition_goal_fit_score(profile, recipe)
        popularity = popularity_map.get(recipe.id, 0.0)

        final_score = (
            0.35 * semantic
            + 0.25 * ingredient_match
            + 0.20 * profile_fit
            + 0.10 * nutrition_goal_fit
            + 0.10 * popularity
        )

        breakdown = {
            "semantic": semantic,
            "ingredient_match": ingredient_match,
            "profile_fit": profile_fit,
            "nutrition_goal_fit": nutrition_goal_fit,
            "popularity_or_feedback": popularity,
        }

        explanation = explainer.build(
            recipe=recipe,
            user_profile=profile,
            breakdown=breakdown,
            query_ingredients=query_ingredients,
        )

        ranked.append(
            {
                "recipe": recipe,
                "score": round(final_score, 4),
                "explanation": explanation,
                "warnings": warnings,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked, blocked


def _blank_profile():
    return SimpleNamespace(
        diet_type="",
        preferred_cuisines=[],
        disliked_ingredients=[],
        max_cooking_time_min=None,
        spice_tolerance=None,
        calorie_target=None,
        protein_target_g=None,
        carbs_target_g=None,
        fat_target_g=None,
        allergies=[],
        health_conditions=[],
    )


def _extract_query_ingredients(query_text: str) -> List[str]:
    if not query_text:
        return []
    return [ing for ing in INGREDIENT_VOCAB if ing in query_text]


def _semantic_score(query_text, recipe):
    if not query_text:
        return 0.0
    haystack = " ".join(
        [
            str(recipe.name or ""),
            str(getattr(recipe, "description", "") or ""),
            str(getattr(recipe, "category", "") or ""),
        ]
    ).lower()
    return _clamp01(fuzz.token_set_ratio(query_text, haystack) / 100.0)


def _ingredient_match_score(query_text, recipe, query_ingredients):
    ingredients_text = (recipe.ingredients or "").lower()

    if query_ingredients:
        hits = 0
        for ingredient in query_ingredients:
            if ingredient in ingredients_text:
                hits += 1
                continue
            if fuzz.partial_ratio(ingredient, ingredients_text) >= 80:
                hits += 1
        return _clamp01(hits / max(len(query_ingredients), 1))

    if not query_text:
        return 0.0
    return _clamp01(fuzz.token_set_ratio(query_text, ingredients_text) / 100.0)


def _profile_fit_score(user_profile, recipe):
    components = []

    diet = (user_profile.diet_type or "").lower()
    if diet in {"vegetarian", "vegan"}:
        components.append(1.0 if recipe.is_vegetarian else 0.0)
    elif diet:
        components.append(1.0)

    cuisines = [c.lower() for c in (user_profile.preferred_cuisines or [])]
    if cuisines and recipe.category:
        components.append(1.0 if recipe.category.lower() in cuisines else 0.4)

    disliked = [d.lower() for d in (user_profile.disliked_ingredients or [])]
    if disliked:
        ingredients_text = (recipe.ingredients or "").lower()
        components.append(0.0 if any(d in ingredients_text for d in disliked) else 1.0)

    if user_profile.max_cooking_time_min and recipe.cooking_time:
        limit = user_profile.max_cooking_time_min
        if recipe.cooking_time <= limit:
            components.append(1.0)
        elif recipe.cooking_time <= int(limit * 1.5):
            components.append(0.5)
        else:
            components.append(0.0)

    if user_profile.spice_tolerance and recipe.spicy_level is not None:
        diff = abs(recipe.spicy_level - user_profile.spice_tolerance)
        if diff == 0:
            components.append(1.0)
        elif diff == 1:
            components.append(0.6)
        else:
            components.append(0.2)

    if not components:
        return 0.5
    return sum(components) / len(components)


def _nutrition_goal_fit_score(user_profile, recipe):
    targets = []

    targets.append(_target_fit(user_profile.calorie_target, recipe.calories))
    targets.append(_target_fit(user_profile.protein_target_g, recipe.protein))
    targets.append(_target_fit(user_profile.carbs_target_g, recipe.carbs))
    targets.append(_target_fit(user_profile.fat_target_g, recipe.fat))

    targets = [score for score in targets if score is not None]
    if not targets:
        return 0.5
    return sum(targets) / len(targets)


def _target_fit(target, value):
    if target is None or value is None:
        return None
    if target <= 0:
        return None
    diff = abs(target - value)
    return _clamp01(1 - (diff / max(target, 1)))


def _popularity_scores(recipe_ids) -> Dict[int, float]:
    if not recipe_ids:
        return {}

    qs = (
        UserRecipeInteraction.objects
        .filter(recipe_id__in=recipe_ids, interaction_type__in=["liked", "saved"])
        .values("recipe_id")
        .annotate(count=Count("id"))
    )

    counts = {row["recipe_id"]: row["count"] for row in qs}
    max_count = max(counts.values(), default=0)
    if max_count <= 0:
        return {recipe_id: 0.0 for recipe_id in recipe_ids}

    return {recipe_id: counts.get(recipe_id, 0) / max_count for recipe_id in recipe_ids}


def _clamp01(value):
    return max(0.0, min(1.0, float(value)))
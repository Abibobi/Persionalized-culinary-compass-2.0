"""
Recipe ranking with profile-aware personalization (Sprint 3).

Ranking formula (when profile available):
  0.30 ingredient_match
  0.15 meal_type_match
  0.15 profile_fit (cuisine, disliked ingredients, cooking time, spice)
  0.15 nutrition_goal_fit
  0.10 diet_match
  0.05 popularity/feedback
  0.10 base_score (time, spice proximity)

Without profile, falls back to query-filter scoring only.
"""

from django.conf import settings

DEFAULT_WEIGHTS = {
    "ingredient": 45,
    "meal": 10,
    "diet": 10,
    "protein": 10,
    "calorie": 10,
    "fat": 7,
    "time": 8,
    "spice": 10,
}

PROFILE_WEIGHTS = {
    "cuisine_match": 12,
    "disliked_penalty": -20,
    "cooking_time_fit": 8,
    "spice_tolerance_fit": 8,
    "calorie_target_fit": 10,
    "protein_target_fit": 8,
    "feedback_boost": 6,
}


def _weights():
    configured = getattr(settings, "RECOMMENDATION_RANKING_WEIGHTS", {}) or {}
    return {
        key: float(configured.get(key, default_value))
        for key, default_value in DEFAULT_WEIGHTS.items()
    }


def _ingredient_overlap_score(query_ingredients, recipe_ingredients):
    if not query_ingredients:
        return 0.0

    recipe_set = {ing.strip().lower() for ing in recipe_ingredients.split(",") if ing.strip()}
    if not recipe_set:
        return 0.0

    matched = 0
    for query_ingredient in query_ingredients:
        query_ingredient = query_ingredient.lower()
        if query_ingredient in recipe_set:
            matched += 1
            continue

        if any(query_ingredient in recipe_item or recipe_item in query_ingredient for recipe_item in recipe_set):
            matched += 1

    return matched / max(len(query_ingredients), 1)


def _matched_ingredients(query_ingredients, recipe_ingredients_text):
    recipe_set = {ing.strip().lower() for ing in recipe_ingredients_text.split(",") if ing.strip()}
    matched = []
    for query_ingredient in query_ingredients:
        query_ingredient = query_ingredient.lower()
        if query_ingredient in recipe_set or any(
            query_ingredient in recipe_item or recipe_item in query_ingredient for recipe_item in recipe_set
        ):
            matched.append(query_ingredient)
    return sorted(set(matched))


def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


# ---------------------------------------------------------------------------
# Profile-aware scoring (Sprint 3)
# ---------------------------------------------------------------------------

def _profile_score(recipe, profile):
    """Extra score from user profile preferences."""
    if profile is None:
        return 0.0

    score = 0.0

    # Preferred cuisines
    preferred = {c.lower() for c in (profile.preferred_cuisines or [])}
    if preferred:
        recipe_tags = {t.lower() for t in (getattr(recipe, "tags", None) or [])}
        cat = recipe.category.lower()
        if preferred & recipe_tags or cat in preferred:
            score += PROFILE_WEIGHTS["cuisine_match"]

    # Disliked ingredients penalty
    disliked = {d.lower() for d in (profile.disliked_ingredients or [])}
    if disliked:
        recipe_text = recipe.ingredients.lower()
        if any(d in recipe_text for d in disliked):
            score += PROFILE_WEIGHTS["disliked_penalty"]

    # Cooking time preference
    if profile.max_cooking_time_min:
        if recipe.cooking_time <= profile.max_cooking_time_min:
            score += PROFILE_WEIGHTS["cooking_time_fit"]

    # Spice tolerance proximity
    if profile.spice_tolerance is not None:
        dist = abs(profile.spice_tolerance - recipe.spicy_level)
        score += _clamp((4 - dist) / 4) * PROFILE_WEIGHTS["spice_tolerance_fit"]

    # Calorie target proximity
    if profile.calorie_target:
        per_meal = profile.calorie_target / 3
        diff = abs(recipe.calories - per_meal)
        score += _clamp((per_meal - diff) / per_meal) * PROFILE_WEIGHTS["calorie_target_fit"]

    # Protein target proximity
    if profile.protein_target_g:
        per_meal = profile.protein_target_g / 3
        diff = abs(recipe.protein - per_meal)
        score += _clamp((per_meal - diff) / max(per_meal, 1)) * PROFILE_WEIGHTS["protein_target_fit"]

    return score


def _feedback_score(recipe, user):
    """Boost recipes the user previously liked; penalise disliked."""
    if user is None or not user.is_authenticated:
        return 0.0
    try:
        from accounts.models import UserRecipeInteraction
        interactions = UserRecipeInteraction.objects.filter(
            user=user, recipe=recipe,
        ).values_list("interaction_type", flat=True)
        boost = 0.0
        for itype in interactions:
            if itype == "liked":
                boost += PROFILE_WEIGHTS["feedback_boost"]
            elif itype == "disliked":
                boost -= PROFILE_WEIGHTS["feedback_boost"]
            elif itype == "cooked":
                boost += PROFILE_WEIGHTS["feedback_boost"] * 0.5
        return boost
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------

def score_recipe(recipe, query_filters, profile=None, user=None):
    weights = _weights()
    score = 0.0

    ingredient_ratio = _ingredient_overlap_score(query_filters.get("ingredients") or [], recipe.ingredients)
    score += ingredient_ratio * weights["ingredient"]

    meal_type = query_filters.get("meal_type")
    if meal_type and recipe.category.lower() == meal_type.lower():
        score += weights["meal"]

    target_vegetarian = query_filters.get("is_vegetarian")
    if target_vegetarian is not None and recipe.is_vegetarian == target_vegetarian:
        score += weights["diet"]

    protein_filter = query_filters.get("protein_filter")
    if protein_filter == "high":
        score += _clamp(recipe.protein / 25) * weights["protein"]
    elif protein_filter == "low":
        score += _clamp((12 - recipe.protein) / 12) * weights["protein"]

    calorie_filter = query_filters.get("calorie_filter")
    if calorie_filter == "low":
        score += _clamp((300 - recipe.calories) / 300) * weights["calorie"]
    elif calorie_filter == "high":
        score += _clamp(recipe.calories / 900) * weights["calorie"]

    fat_filter = query_filters.get("fat_filter")
    if fat_filter == "low":
        score += _clamp((20 - recipe.fat) / 20) * weights["fat"]
    elif fat_filter == "high":
        score += _clamp(recipe.fat / 30) * weights["fat"]

    time_limit = query_filters.get("cooking_time_filter")
    if time_limit:
        if recipe.cooking_time <= time_limit:
            score += weights["time"]
        else:
            score += _clamp((time_limit + 15 - recipe.cooking_time) / 15) * weights["time"]

    target_spice = query_filters.get("spicy_level")
    if target_spice is not None:
        distance = abs(target_spice - recipe.spicy_level)
        score += _clamp((4 - distance) / 4) * weights["spice"]

    # Profile-aware additions (Sprint 3)
    score += _profile_score(recipe, profile)
    score += _feedback_score(recipe, user)

    return round(score, 3)


def rank_recipes(recipes, query_filters, profile=None, user=None):
    scored = [
        (recipe, score_recipe(recipe, query_filters, profile=profile, user=user))
        for recipe in recipes
    ]
    scored.sort(key=lambda item: (-item[1], item[0].id))
    return scored


def explain_recipe_match(recipe, query_filters, profile=None):
    reasons = []
    matched_ingredients = _matched_ingredients(query_filters.get("ingredients") or [], recipe.ingredients)

    if matched_ingredients:
        reasons.append(f"Matched ingredients: {', '.join(matched_ingredients)}")

    meal_type = query_filters.get("meal_type")
    if meal_type and recipe.category.lower() == meal_type.lower():
        reasons.append(f"Matches meal type: {meal_type}")

    target_vegetarian = query_filters.get("is_vegetarian")
    if target_vegetarian is True and recipe.is_vegetarian:
        reasons.append("Fits vegetarian preference")
    elif target_vegetarian is False and not recipe.is_vegetarian:
        reasons.append("Fits non-vegetarian preference")

    limit = query_filters.get("cooking_time_filter")
    if limit:
        if recipe.cooking_time <= limit:
            reasons.append(f"Within cooking time limit ({recipe.cooking_time} <= {limit} min)")
        else:
            reasons.append(f"Slightly above preferred cooking time ({recipe.cooking_time} min)")

    if query_filters.get("protein_filter") == "high" and recipe.protein >= 20:
        reasons.append("Good protein level for high-protein request")
    if query_filters.get("calorie_filter") == "low" and recipe.calories <= 300:
        reasons.append("Suitable for low-calorie request")
    if query_filters.get("fat_filter") == "low" and recipe.fat <= 15:
        reasons.append("Suitable for low-fat request")

    # Profile-based explanations
    if profile:
        preferred = {c.lower() for c in (profile.preferred_cuisines or [])}
        recipe_tags = {t.lower() for t in (getattr(recipe, "tags", None) or [])}
        overlap = preferred & recipe_tags
        if overlap:
            reasons.append(f"Matches preferred cuisine: {', '.join(overlap)}")
        if profile.max_cooking_time_min and recipe.cooking_time <= profile.max_cooking_time_min:
            reasons.append(f"Fits your max cooking time ({profile.max_cooking_time_min} min)")

    return {
        "matched_ingredients": matched_ingredients,
        "reasons": reasons,
    }

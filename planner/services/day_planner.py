"""
Day meal-plan generator.

Algorithm:
1. Compute per-meal calorie/macro budgets from user profile targets.
2. Build safe candidate pools per meal category (uses safety engine).
3. Rank by profile fit + variety + prep-time.
4. Select combination minimising deviation from targets.
5. Produce totals, warnings, and shopping list.
"""

import datetime
import random

from django.db.models import Q

from accounts.models import UserProfile
from planner.models import MealPlan, MealPlanItem
from recipes.models import Recipe
from safety.services.rules_engine import evaluate_recipe_safety

# Meal calorie distribution ratios
MEAL_RATIOS = {
    3: {"breakfast": 0.30, "lunch": 0.40, "dinner": 0.30},
    4: {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snack": 0.10},
}

# Category mapping (recipe.category -> meal type)
CATEGORY_MAP = {
    "breakfast": ["breakfast"],
    "lunch": ["lunch", "dinner", "snack"],
    "dinner": ["lunch", "dinner"],
    "snack": ["snack", "breakfast"],
}


def generate_meal_plan(user, date=None, day_type="normal", num_meals=4):
    """Create or replace a MealPlan for *user* on *date*."""
    date = date or datetime.date.today()
    profile, _ = UserProfile.objects.get_or_create(user=user)
    target_cal = profile.calorie_target or 2000

    slots = list(MEAL_RATIOS.get(num_meals, MEAL_RATIOS[4]).items())

    # Get recently used recipe IDs (last 3 days) to avoid repetition
    recent_ids = set(
        MealPlanItem.objects.filter(
            meal_plan__user=user,
            meal_plan__date__gte=date - datetime.timedelta(days=3),
        )
        .exclude(meal_plan__date=date)
        .values_list("recipe_id", flat=True)
    )

    all_recipes = list(Recipe.objects.all())
    plan_warnings = []
    selected_items = []

    for meal_type, ratio in slots:
        budget_cal = int(target_cal * ratio)
        candidates = _candidates_for_meal(meal_type, all_recipes, profile, recent_ids)

        if not candidates:
            plan_warnings.append(f"No suitable recipes for {meal_type}.")
            continue

        best = _pick_best(candidates, budget_cal, day_type, profile)
        if best is None:
            plan_warnings.append(f"Could not find a good fit for {meal_type}.")
            continue

        recipe, item_warnings = best
        servings = max(0.5, min(2.0, round(budget_cal / max(recipe.calories, 1), 1)))
        selected_items.append((meal_type, recipe, servings))
        plan_warnings.extend(item_warnings)

    # Persist
    MealPlan.objects.filter(user=user, date=date).delete()
    plan = MealPlan.objects.create(
        user=user,
        date=date,
        day_type=day_type,
        num_meals=num_meals,
        target_calories=target_cal,
        warnings=plan_warnings,
    )

    for meal_type, recipe, servings in selected_items:
        item = MealPlanItem(meal_plan=plan, meal_type=meal_type, recipe=recipe, servings=servings)
        item.snapshot_nutrition()
        item.save()

    plan.recalculate_totals()
    return plan


def regenerate_meal_item(plan, item_id):
    """Replace a single item in an existing plan while preserving totals."""
    item = plan.items.get(id=item_id)
    profile, _ = UserProfile.objects.get_or_create(user=plan.user)
    all_recipes = list(Recipe.objects.all())
    recent_ids = {item.recipe_id}  # exclude current recipe

    candidates = _candidates_for_meal(item.meal_type, all_recipes, profile, recent_ids)
    if not candidates:
        return None

    budget_cal = int((plan.target_calories or 2000) * 0.30)
    best = _pick_best(candidates, budget_cal, plan.day_type, profile)
    if best is None:
        return None

    recipe, _ = best
    item.recipe = recipe
    item.servings = max(0.5, min(2.0, round(budget_cal / max(recipe.calories, 1), 1)))
    item.snapshot_nutrition()
    item.save()
    plan.recalculate_totals()
    return item


def generate_shopping_list(plan):
    """Build a combined ingredient list from all plan items."""
    shopping = {}
    for item in plan.items.select_related("recipe"):
        for raw in item.recipe.ingredients.split(","):
            ing = raw.strip().lower()
            if ing:
                shopping[ing] = shopping.get(ing, 0) + item.servings
    return [{"ingredient": k, "servings": round(v, 1)} for k, v in sorted(shopping.items())]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _candidates_for_meal(meal_type, recipes, profile, exclude_ids):
    """Return recipes suitable for *meal_type* that pass safety checks."""
    # Map meal_type to acceptable recipe categories
    ok_categories = CATEGORY_MAP.get(meal_type, [meal_type])
    pool = [r for r in recipes if r.category.lower() in ok_categories and r.id not in exclude_ids]

    safe = []
    for r in pool:
        ws = evaluate_recipe_safety(r, profile)
        if any(w["severity"] == "danger" for w in ws):
            continue
        info_warnings = [w for w in ws if w["severity"] in ("warning", "info")]
        safe.append((r, [w["message"] for w in info_warnings]))

    return safe


def _pick_best(candidates, budget_cal, day_type, profile):
    """Score candidates and return the best (recipe, warnings) tuple."""
    if not candidates:
        return None

    def score(r):
        cal_diff = abs(r.calories - budget_cal)
        cal_score = max(0, 100 - cal_diff * 0.1)

        time_score = 0
        if profile.max_cooking_time_min and r.cooking_time <= profile.max_cooking_time_min:
            time_score = 20

        protein_score = 0
        if day_type == "workout" and r.protein >= 20:
            protein_score = 30
        elif day_type == "low_carb" and r.carbs <= 30:
            protein_score = 30

        jitter = random.random() * 5  # variety
        return cal_score + time_score + protein_score + jitter

    scored = [(score(r), r, ws) for r, ws in candidates]
    scored.sort(key=lambda x: -x[0])
    _, recipe, warnings = scored[0]
    return recipe, warnings

"""
Safety rules engine – evaluates recipes against user health profiles.

Two evaluation modes:
1. Database rules (SafetyRule model, admin-configurable)
2. Built-in heuristic rules (allergies, conditions, diet integrity)
"""

from ..models import SafetyRule


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_recipe_safety(recipe, user_profile):
    """Return a list of warning dicts for *recipe* given *user_profile*."""
    warnings = []

    # 1) Database-driven rules
    for rule in SafetyRule.objects.filter(is_active=True):
        w = _check_db_rule(rule, recipe, user_profile)
        if w:
            warnings.append(w)

    # 2) Built-in checks
    warnings.extend(_check_allergies(recipe, user_profile))
    warnings.extend(_check_health_conditions(recipe, user_profile))
    warnings.extend(_check_diet_integrity(recipe, user_profile))

    return warnings


def filter_dangerous_recipes(recipes, user_profile):
    """
    Partition *recipes* into safe and blocked lists.
    Returns (safe_with_warnings, blocked_with_reasons).
    """
    safe, blocked = [], []
    for recipe in recipes:
        ws = evaluate_recipe_safety(recipe, user_profile)
        danger = [w for w in ws if w["severity"] == "danger"]
        if danger:
            blocked.append({
                "recipe_id": recipe.id,
                "recipe_name": recipe.name,
                "reasons": [w["message"] for w in danger],
            })
        else:
            safe.append((recipe, ws))
    return safe, blocked


# ---------------------------------------------------------------------------
# Database rule checker
# ---------------------------------------------------------------------------

def _check_db_rule(rule, recipe, user_profile):
    cond = rule.condition or {}
    rtype = rule.rule_type

    if rtype == "allergen_contains":
        return _db_allergen(rule, cond, recipe, user_profile)
    if rtype == "nutrient_threshold":
        return _db_nutrient(rule, cond, recipe, user_profile)
    if rtype == "ingredient_conflict":
        return _db_ingredient(rule, cond, recipe, user_profile)
    return None


def _db_allergen(rule, cond, recipe, user_profile):
    allergen = (cond.get("allergen") or "").lower()
    if not allergen:
        return None
    user_allergies = {a.lower() for a in (user_profile.allergies or [])}
    if allergen not in user_allergies:
        return None
    recipe_text = recipe.ingredients.lower()
    recipe_allergens = {a.lower() for a in (getattr(recipe, "allergens", None) or [])}
    if allergen in recipe_text or allergen in recipe_allergens:
        return _warning(rule, recipe_name=recipe.name, allergen=allergen)
    return None


def _db_nutrient(rule, cond, recipe, user_profile):
    nutrient = cond.get("nutrient")
    threshold = cond.get("max_value")
    hc = (cond.get("health_condition") or "").lower()
    if not all([nutrient, threshold, hc]):
        return None
    user_conds = {c.lower() for c in (user_profile.health_conditions or [])}
    if hc not in user_conds:
        return None
    val = getattr(recipe, nutrient, None)
    if val is not None and val > threshold:
        return _warning(rule, recipe_name=recipe.name, nutrient=nutrient, value=val, threshold=threshold)
    return None


def _db_ingredient(rule, cond, recipe, user_profile):
    ingredient = (cond.get("ingredient") or "").lower()
    hc = (cond.get("health_condition") or "").lower()
    if not ingredient or not hc:
        return None
    user_conds = {c.lower() for c in (user_profile.health_conditions or [])}
    if hc not in user_conds:
        return None
    if ingredient in recipe.ingredients.lower():
        return _warning(rule, recipe_name=recipe.name, ingredient=ingredient)
    return None


def _warning(rule, **fmt):
    try:
        msg = rule.message_template.format(**fmt)
    except KeyError:
        msg = rule.message_template
    return {"rule_key": rule.key, "severity": rule.severity, "message": msg}


# ---------------------------------------------------------------------------
# Built-in heuristic checks
# ---------------------------------------------------------------------------

def _check_allergies(recipe, user_profile):
    out = []
    for allergy in (user_profile.allergies or []):
        al = allergy.lower()
        recipe_text = recipe.ingredients.lower()
        allergen_list = {a.lower() for a in (getattr(recipe, "allergens", None) or [])}
        if al in recipe_text or al in allergen_list:
            out.append({
                "rule_key": f"allergy_{al}",
                "severity": "danger",
                "message": f"Contains '{allergy}' which is in your allergy list.",
            })
    return out


def _check_health_conditions(recipe, user_profile):
    out = []
    conds = {c.lower() for c in (user_profile.health_conditions or [])}

    if conds & {"diabetic", "diabetes"}:
        if recipe.carbs > 60:
            out.append({
                "rule_key": "diabetic_high_carbs",
                "severity": "warning",
                "message": f"High carbs ({recipe.carbs}g) – may not suit a diabetic diet.",
            })

    if conds & {"hypertension", "high blood pressure"}:
        sodium = getattr(recipe, "sodium_mg", None)
        if sodium and sodium > 600:
            out.append({
                "rule_key": "hypertension_sodium",
                "severity": "warning",
                "message": f"High sodium ({sodium}mg) – may not suit hypertension.",
            })

    return out


def _check_diet_integrity(recipe, user_profile):
    out = []
    diet = (user_profile.diet_type or "").lower()

    if diet == "vegan":
        is_vegan = getattr(recipe, "is_vegan", None)
        if is_vegan is False:
            out.append({
                "rule_key": "diet_vegan_violation",
                "severity": "danger",
                "message": "Not vegan-compatible.",
            })
        elif not recipe.is_vegetarian:
            out.append({
                "rule_key": "diet_vegan_violation",
                "severity": "danger",
                "message": "Contains non-vegetarian ingredients (not vegan).",
            })

    elif diet == "vegetarian" and not recipe.is_vegetarian:
        out.append({
            "rule_key": "diet_vegetarian_violation",
            "severity": "danger",
            "message": "Contains non-vegetarian ingredients.",
        })

    return out

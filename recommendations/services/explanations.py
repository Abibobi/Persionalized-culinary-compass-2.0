class ExplanationBuilder:
    def build(self, recipe, user_profile, breakdown, query_ingredients=None):
        reasons = []

        diet = (user_profile.diet_type or "").lower()
        if diet in {"vegan", "vegetarian"} and recipe.is_vegetarian:
            reasons.append(f"matches your {diet} diet")

        cuisines = [c.lower() for c in (user_profile.preferred_cuisines or [])]
        if cuisines and recipe.category:
            if recipe.category.lower() in cuisines:
                reasons.append(f"{recipe.category} cuisine preference")

        disliked = [d.lower() for d in (user_profile.disliked_ingredients or [])]
        if disliked:
            ingredients_text = (recipe.ingredients or "").lower()
            if not any(d in ingredients_text for d in disliked):
                reasons.append("avoids your disliked ingredients")

        if user_profile.max_cooking_time_min and recipe.cooking_time:
            if recipe.cooking_time <= user_profile.max_cooking_time_min:
                reasons.append(f"under {user_profile.max_cooking_time_min} min prep")

        if recipe.protein is not None and recipe.protein >= 20:
            reasons.append(f"high protein ({int(recipe.protein)}g)")

        if user_profile.calorie_target and recipe.calories:
            diff = abs(user_profile.calorie_target - recipe.calories)
            if diff <= max(50, int(user_profile.calorie_target * 0.1)):
                reasons.append(f"near your calorie target ({recipe.calories} kcal)")

        if query_ingredients:
            ingredients_text = (recipe.ingredients or "").lower()
            matched = [ing for ing in query_ingredients if ing in ingredients_text]
            if matched:
                reasons.append("includes " + ", ".join(matched[:2]))

        if not reasons:
            reasons.append("balanced macros and strong overall match")

        return {"why": ", ".join(reasons[:3])}

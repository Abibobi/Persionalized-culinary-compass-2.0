def profile_score(user_profile, recipe):
    score = 0

    # calorie target proximity
    if user_profile.calorie_target and recipe.calories:
        diff = abs(user_profile.calorie_target - recipe.calories)
        score += max(0, 50 - diff / 10)

    # cooking time preference
    if user_profile.max_cooking_time_min and recipe.cooking_time:
        if recipe.cooking_time <= user_profile.max_cooking_time_min:
            score += 15

    # diet preference
    if user_profile.diet_type in {"vegetarian", "vegan"} and recipe.is_vegetarian:
        score += 20

    # preferred cuisines (if you store in profile)
    if user_profile.preferred_cuisines and recipe.category:
        if recipe.category.lower() in [c.lower() for c in user_profile.preferred_cuisines]:
            score += 10

    return score
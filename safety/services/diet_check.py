def check_diet(user_profile, recipe):
    warnings = []
    diet = user_profile.diet_type

    # if vegetarian/vegan but recipe is not vegetarian
    if diet in {"vegetarian", "vegan"} and not recipe.is_vegetarian:
        warnings.append("Recipe may not meet vegetarian/vegan preference")

    return warnings
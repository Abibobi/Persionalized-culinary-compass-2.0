def check_allergies(user_profile, recipe):
    warnings = []

    # profile allergies list (strings)
    allergies = [a.lower() for a in (user_profile.allergies or [])]

    # recipe ingredients string
    ingredients_text = (recipe.ingredients or "").lower()

    for allergy in allergies:
        if allergy and allergy in ingredients_text:
            warnings.append(f"Contains allergen: {allergy}")

    return warnings
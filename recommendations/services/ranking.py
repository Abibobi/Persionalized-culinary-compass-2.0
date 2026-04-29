def score_recipe(recipe):
    """
    Simple baseline score:
    - higher protein is better
    - lower calories is better
    """
    protein = recipe.protein or 0
    calories = recipe.calories or 0

    return (protein * 2) - (calories / 100)
from .parser import parse_query
from .ranking import rank_recipes


def _ingredient_match(query_ingredients, recipe_ingredients):
    recipe_set = {item.lower() for item in recipe_ingredients}
    for ingredient in query_ingredients:
        ingredient = ingredient.lower()
        if ingredient in recipe_set:
            return True
        if any(ingredient in recipe_item or recipe_item in ingredient for recipe_item in recipe_set):
            return True
    return False


def filter_recipes_by_ingredients_and_diet(
    recipes,
    ingredients,
    calorie_filter=None,
    protein_filter=None,
    fat_filter=None,
    cooking_time_filter=None,
    meal_type=None,
    is_vegetarian=None,
    spicy_level=None,
):
    filtered_recipes = []

    for recipe in recipes:
        recipe_ingredients = [ing.strip().lower() for ing in recipe.ingredients.split(",") if ing.strip()]

        if ingredients and not _ingredient_match(ingredients, recipe_ingredients):
            continue

        if calorie_filter == "low" and recipe.calories > 200:
            continue
        if calorie_filter == "high" and recipe.calories < 800:
            continue

        if protein_filter == "high" and recipe.protein < 20:
            continue
        if protein_filter == "low" and recipe.protein > 10:
            continue

        if fat_filter == "low" and recipe.fat > 15:
            continue
        if fat_filter == "high" and recipe.fat < 10:
            continue

        if meal_type and recipe.category.lower() != meal_type.lower():
            continue

        if is_vegetarian is not None and recipe.is_vegetarian != is_vegetarian:
            continue

        if spicy_level is not None and not (spicy_level - 1 <= recipe.spicy_level <= spicy_level + 1):
            continue

        if cooking_time_filter and recipe.cooking_time > cooking_time_filter:
            continue

        filtered_recipes.append(recipe)

    return filtered_recipes


def search_recipe_ids(user_query, queryset):
    query_data = parse_query(user_query)
    filtered_recipes = filter_recipes_by_ingredients_and_diet(queryset, **query_data)
    ranked = rank_recipes(filtered_recipes, query_data)
    return [recipe.id for recipe, _ in ranked], query_data

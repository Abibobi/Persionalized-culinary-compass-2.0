import spacy
import logging
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Recipe
from spacy.matcher import PhraseMatcher

# Load spaCy model
nlp_spacy = spacy.load("en_core_web_sm")
logger = logging.getLogger(__name__)

common_ingredients = list(set([
    "onion", "garlic", "ginger", "tomato", "potato", "carrot", "bell pepper", "spinach", 
    "kale", "broccoli", "cauliflower", "zucchini", "eggplant", "cucumber", "lettuce", 
    "avocado", "green beans", "peas", "corn", "mushrooms", "cabbage", "radish", "pumpkin", 
    "bitter gourd", "snake gourd", "bottle gourd", "sweet potato", "yam", "squash", "chard", 
    "celery", "leeks", "shallots", "fennel", "beetroot", "channa", "mint", "oats", "chickpeas",
    "beets", "fresh herbs", "dried herbs", "salt", "pepper", "olive oil", "vegetable oil", 
    "coconut oil", "ghee", "butter", "honey", "sugar", "brown sugar", "maple syrup", "vinegar", 
    "soy sauce", "Worcestershire sauce", "mustard", "ketchup", "hot sauce", "wheat flour", "tahini", 
    "nut butter", "chia seeds", "flaxseeds", "sesame seeds", "nuts", "coconut", "dried fruits", 
    "quinoa", "couscous", "rice", "pasta", "lentils", "beans", "tofu", "tempeh", "fish sauce", 
    "coconut milk", "chicken broth", "vegetable broth", "eggs", "cheese", "cream", "yogurt", 
    "milk", "buttermilk", "heavy cream", "chicken", "baking powder", "baking soda", "flour", 
    "cornstarch", "cocoa powder", "chocolate chips", "vanilla extract", "cinnamon", "nutmeg", 
    "cardamom", "cloves", "curry powder", "paprika", "chili powder", "cumin", "coriander", "allspice", 
    "saffron", "bay leaves", "granola", "pesto", "marinara sauce", "salsa", "ridge gourd", "drumstick", 
    "taro", "kohlrabi", "pointed gourd", "Indian squash", "methi", "palak", "amaranth", "colocasia", 
    "bamboo shoots"
]))


def filter_recipes_by_ingredients_and_diet(recipes, ingredients, calorie_filter=None, protein_filter=None, 
                                           fat_filter=None, cooking_time_filter=None, meal_type=None, 
                                           is_vegetarian=None, spicy_level=None):
    filtered_recipes = []
    
    for recipe in recipes:
        recipe_ingredients = [ing.strip().lower() for ing in recipe.ingredients.split(',')]
        if ingredients and not any(ingredient.lower() in recipe_ingredients for ingredient in ingredients):
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

def parse_query(user_query):
    doc = nlp_spacy(user_query.lower())
    ingredients = set()
    calorie_filter, protein_filter, fat_filter, cooking_time_filter = None, None, None, None
    meal_type, is_vegetarian, spicy_level = None, None, None
    
    if "high protein" in user_query:
        protein_filter = "high"
    if "low protein" in user_query:
        protein_filter = "low"
    if "low calorie" in user_query:
        calorie_filter = "low"
    if "high calorie" in user_query:
        calorie_filter = "high"
    if "low fat" in user_query:
        fat_filter = "low"
    if "high fat" in user_query:
        fat_filter = "high"
    if "breakfast" in user_query:
        meal_type = "breakfast"
    if "lunch" in user_query:
        meal_type = "lunch"
    if "dinner" in user_query:
        meal_type = "dinner"
    if "snack" in user_query:
        meal_type = "snack"
    if "vegetarian" in user_query:
        is_vegetarian = True
    if "non-vegetarian" in user_query or "meat" in user_query:
        is_vegetarian = False
    if "spicy" in user_query:
        spicy_level = 4
    if "mild" in user_query:
        spicy_level = 2
    if "medium" in user_query:
        spicy_level = 3
    for token in doc:
        if token.like_num:
            next_token = doc[token.i + 1] if token.i + 1 < len(doc) else None
            if next_token and next_token.text in ["minutes", "minute"]:
                cooking_time_filter = int(token.text)
    from spacy.matcher import PhraseMatcher
    matcher = PhraseMatcher(nlp_spacy.vocab)
    matcher.add("Ingredients", [nlp_spacy.make_doc(ing) for ing in common_ingredients])
    matches = matcher(doc)
    for match_id, start, end in matches:
        ingredients.add(doc[start:end].text.lower())
    return {
        "ingredients": list(ingredients), "calorie_filter": calorie_filter,
        "protein_filter": protein_filter, "fat_filter": fat_filter,
        "cooking_time_filter": cooking_time_filter, "meal_type": meal_type,
        "is_vegetarian": is_vegetarian, "spicy_level": spicy_level
    }

def get_recipes(request):
    user_query = request.GET.get('query', '').lower()
    if "more"  in user_query and 'filtered_recipes' in request.session:
        filtered_recipes = request.session['filtered_recipes']
        page_number = request.session.get('page_number', 1) + 1
    else:
        request.session['page_number'] = 1
        query_data = parse_query(user_query)
        all_recipes = Recipe.objects.all()
        filtered_recipes = filter_recipes_by_ingredients_and_diet(
            all_recipes, **query_data)
        request.session['filtered_recipes'] = [r.id for r in filtered_recipes]
        page_number = 1
    paginator = Paginator(Recipe.objects.filter(id__in=request.session['filtered_recipes']), 5)
    try:
        recipes_page = paginator.page(page_number)
    except:
        return JsonResponse({'message': 'No more recipes found for your search query.'}, status=404)
    recipe_data = [{
        'id': recipe.id, 'name': recipe.name, 'description': recipe.description
    } for recipe in recipes_page]
    request.session['page_number'] = page_number
    return JsonResponse({'recipes': recipe_data})

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return JsonResponse({"recipe": {
        "name": recipe.name, "description": recipe.description,
        "ingredients": recipe.ingredients, "instructions": recipe.instructions,
        "category": recipe.category, "protein": recipe.protein,
        "carbs": recipe.carbs, "fat": recipe.fat, "fiber": recipe.fiber,
        "vitamins": recipe.vitamins, "calories": recipe.calories,
        "cooking_time": recipe.cooking_time, "spicy_level": recipe.spicy_level,
        "is_vegetarian": recipe.is_vegetarian
    }})

def base(request):
    return render(request, "base.html")

def chatbot_view(request):
    return render(request, "chatbot.html")

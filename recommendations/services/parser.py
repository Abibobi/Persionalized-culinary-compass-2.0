import difflib
import logging
import re

import spacy
from spacy.matcher import PhraseMatcher

logger = logging.getLogger(__name__)

try:
    from rapidfuzz import fuzz, process
except ImportError:  # pragma: no cover
    fuzz = None
    process = None


COMMON_INGREDIENTS = sorted(
    {
        "onion",
        "garlic",
        "ginger",
        "tomato",
        "potato",
        "carrot",
        "bell pepper",
        "spinach",
        "kale",
        "broccoli",
        "cauliflower",
        "zucchini",
        "eggplant",
        "cucumber",
        "lettuce",
        "avocado",
        "green beans",
        "peas",
        "corn",
        "mushrooms",
        "cabbage",
        "radish",
        "pumpkin",
        "bitter gourd",
        "snake gourd",
        "bottle gourd",
        "sweet potato",
        "yam",
        "squash",
        "chard",
        "celery",
        "leeks",
        "shallots",
        "fennel",
        "beetroot",
        "channa",
        "mint",
        "oats",
        "chickpeas",
        "beets",
        "fresh herbs",
        "dried herbs",
        "salt",
        "pepper",
        "olive oil",
        "vegetable oil",
        "coconut oil",
        "ghee",
        "butter",
        "honey",
        "sugar",
        "brown sugar",
        "maple syrup",
        "vinegar",
        "soy sauce",
        "worcestershire sauce",
        "mustard",
        "ketchup",
        "hot sauce",
        "wheat flour",
        "tahini",
        "nut butter",
        "chia seeds",
        "flaxseeds",
        "sesame seeds",
        "nuts",
        "coconut",
        "dried fruits",
        "quinoa",
        "couscous",
        "rice",
        "pasta",
        "lentils",
        "beans",
        "tofu",
        "tempeh",
        "fish sauce",
        "coconut milk",
        "chicken broth",
        "vegetable broth",
        "eggs",
        "cheese",
        "cream",
        "yogurt",
        "milk",
        "buttermilk",
        "heavy cream",
        "chicken",
        "baking powder",
        "baking soda",
        "flour",
        "cornstarch",
        "cocoa powder",
        "chocolate chips",
        "vanilla extract",
        "cinnamon",
        "nutmeg",
        "cardamom",
        "cloves",
        "curry powder",
        "paprika",
        "chili powder",
        "cumin",
        "coriander",
        "allspice",
        "saffron",
        "bay leaves",
        "granola",
        "pesto",
        "marinara sauce",
        "salsa",
        "ridge gourd",
        "drumstick",
        "taro",
        "kohlrabi",
        "pointed gourd",
        "indian squash",
        "methi",
        "palak",
        "amaranth",
        "colocasia",
        "bamboo shoots",
    }
)

TYPO_NORMALIZATION_MAP = {
    "vegtarian": "vegetarian",
    "vegitarian": "vegetarian",
    "vegitarian": "vegetarian",
    "vegane": "vegan",
    "diner": "dinner",
    "breakfst": "breakfast",
    "luch": "lunch",
    "onyun": "onion",
    "onin": "onion",
    "garlec": "garlic",
    "tomoto": "tomato",
    "chikn": "chicken",
    "protien": "protein",
    "caloriee": "calorie",
    "spciy": "spicy",
    "miled": "mild",
    "mediam": "medium",
    "minut": "minute",
    "minuts": "minutes",
    "mins": "minutes",
}

SYNONYM_NORMALIZATION_MAP = {
    "nonveg": "non vegetarian",
    "non veg": "non vegetarian",
    "veggie": "vegetarian",
    "plant based": "vegan",
    "plantbased": "vegan",
    "supper": "dinner",
    "midday": "lunch",
    "kcal": "calorie",
}

INGREDIENT_STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "with",
    "without",
    "under",
    "over",
    "very",
    "please",
    "recipe",
    "recipes",
    "meal",
    "meals",
    "show",
    "give",
    "want",
    "need",
    "make",
    "cook",
    "healthy",
    "high",
    "low",
    "protein",
    "fat",
    "calorie",
    "breakfast",
    "lunch",
    "dinner",
    "snack",
    "vegetarian",
    "vegan",
    "non",
    "vegetarian",
    "spicy",
    "mild",
    "medium",
    "minute",
    "minutes",
}


def _load_nlp():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy model 'en_core_web_sm' not found, falling back to blank English model.")
        return spacy.blank("en")


def _build_ingredient_matcher(nlp_model):
    matcher = PhraseMatcher(nlp_model.vocab, attr="LOWER")
    matcher.add("Ingredients", [nlp_model.make_doc(ing) for ing in COMMON_INGREDIENTS])
    return matcher


nlp_spacy = _load_nlp()
ingredient_matcher = _build_ingredient_matcher(nlp_spacy)


def normalize_query_text(user_query):
    query = (user_query or "").strip().lower()
    query = query.replace("-", " ")
    query = re.sub(r"[^a-z0-9\s]", " ", query)
    query = re.sub(r"\s+", " ", query).strip()

    for typo, fixed in TYPO_NORMALIZATION_MAP.items():
        query = re.sub(rf"\b{re.escape(typo)}\b", fixed, query)

    for synonym, fixed in SYNONYM_NORMALIZATION_MAP.items():
        query = re.sub(rf"\b{re.escape(synonym)}\b", fixed, query)

    query = re.sub(r"\s+", " ", query).strip()
    return query


def _extract_exact_ingredients(doc):
    matches = ingredient_matcher(doc)
    return {doc[start:end].text.lower() for _, start, end in matches}


def _fuzzy_match_term(term):
    if process and fuzz:
        match = process.extractOne(term, COMMON_INGREDIENTS, scorer=fuzz.ratio, score_cutoff=87)
        return match[0] if match else None

    fallback = difflib.get_close_matches(term, COMMON_INGREDIENTS, n=1, cutoff=0.9)
    return fallback[0] if fallback else None


def _extract_fuzzy_ingredients(normalized_query, existing_ingredients):
    words = re.findall(r"[a-z]+", normalized_query)
    candidate_terms = set()

    for word in words:
        if len(word) > 2 and word not in INGREDIENT_STOP_WORDS:
            candidate_terms.add(word)

    for i in range(len(words) - 1):
        phrase = f"{words[i]} {words[i + 1]}"
        if words[i] not in INGREDIENT_STOP_WORDS and words[i + 1] not in INGREDIENT_STOP_WORDS:
            candidate_terms.add(phrase)

    fuzzy_hits = set()
    for term in candidate_terms:
        if term in existing_ingredients or term in COMMON_INGREDIENTS:
            if term in COMMON_INGREDIENTS:
                fuzzy_hits.add(term)
            continue

        matched = _fuzzy_match_term(term)
        if matched:
            fuzzy_hits.add(matched)

    return fuzzy_hits


def _extract_cooking_time(doc, normalized_query):
    regex_match = re.search(r"\b(\d+)\s*(?:minute|minutes|min)\b", normalized_query)
    if regex_match:
        return int(regex_match.group(1))

    for token in doc:
        if token.like_num:
            next_token = doc[token.i + 1] if token.i + 1 < len(doc) else None
            if next_token and next_token.text in {"minute", "minutes", "min"}:
                return int(token.text)

    return None


def parse_query(user_query):
    normalized_query = normalize_query_text(user_query)
    doc = nlp_spacy(normalized_query)

    ingredients = _extract_exact_ingredients(doc)
    ingredients.update(_extract_fuzzy_ingredients(normalized_query, ingredients))

    calorie_filter = None
    protein_filter = None
    fat_filter = None
    meal_type = None
    is_vegetarian = None
    spicy_level = None

    if "high protein" in normalized_query or "protein rich" in normalized_query:
        protein_filter = "high"
    if "low protein" in normalized_query:
        protein_filter = "low"

    if "low calorie" in normalized_query:
        calorie_filter = "low"
    if "high calorie" in normalized_query:
        calorie_filter = "high"

    if "low fat" in normalized_query:
        fat_filter = "low"
    if "high fat" in normalized_query:
        fat_filter = "high"

    for meal in ("breakfast", "lunch", "dinner", "snack"):
        if meal in normalized_query:
            meal_type = meal
            break

    if "non vegetarian" in normalized_query or "meat" in normalized_query:
        is_vegetarian = False
    elif "vegetarian" in normalized_query or "vegan" in normalized_query:
        is_vegetarian = True

    if "spicy" in normalized_query:
        spicy_level = 4
    elif "mild" in normalized_query:
        spicy_level = 2
    elif "medium" in normalized_query:
        spicy_level = 3

    cooking_time_filter = _extract_cooking_time(doc, normalized_query)

    return {
        "ingredients": sorted(ingredients),
        "calorie_filter": calorie_filter,
        "protein_filter": protein_filter,
        "fat_filter": fat_filter,
        "cooking_time_filter": cooking_time_filter,
        "meal_type": meal_type,
        "is_vegetarian": is_vegetarian,
        "spicy_level": spicy_level,
    }

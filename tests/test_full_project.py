"""
Comprehensive test suite for Personalized Culinary Compass 2.0
Covers Sprints 0-5: Auth, Search, Ranking, Safety, Meal Planning

Run with: python manage.py test tests.test_full_project --verbosity=2
"""
import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserProfile, UserRecipeInteraction
from recipes.models import Recipe
from recommendations.models import SearchLog
from recommendations.services.normalizer import normalize_query
from recommendations.services.parser import parse_filters
from recommendations.services.ranking import rank_recipes
from recommendations.services.explanations import ExplanationBuilder
from safety.models import SafetyRule
from safety.services.rules_engine import evaluate_recipe_safety, filter_dangerous_recipes
from planner.models import MealPlan, MealPlanItem
from planner.services.day_planner import generate_meal_plan, regenerate_meal_item, generate_shopping_list

User = get_user_model()


# ─── Helpers ───
def make_user(username, diet="omnivore", allergies=None, conditions=None, **kwargs):
    user = User.objects.create_user(username=username, email=f"{username}@test.com", password="test1234!")
    p = user.profile
    p.diet_type = diet
    p.allergies = allergies or []
    p.health_conditions = conditions or []
    p.calorie_target = kwargs.get("calorie_target", 2000)
    p.protein_target_g = kwargs.get("protein_target_g", 120)
    p.max_cooking_time_min = kwargs.get("max_cooking_time_min", 45)
    p.spice_tolerance = kwargs.get("spice_tolerance", 3)
    p.onboarding_completed = True
    p.save()
    return user


def make_recipe(name, category="dinner", calories=400, protein=20, carbs=40, fat=15,
                ingredients="onion, garlic, tomato", is_vegetarian=False, cooking_time=30,
                spicy_level=2):
    return Recipe.objects.create(
        name=name, description=f"Test {name}", ingredients=ingredients,
        category=category, protein=protein, carbs=carbs, fat=fat, fiber=5,
        vitamins={"vitamin c": 10}, calories=calories, cooking_time=cooking_time,
        spicy_level=spicy_level, instructions="Step 1. Cook.", is_vegetarian=is_vegetarian,
    )


def get_auth_client(user):
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return client


# ═══════════════════════════════════════════════════════════════
# SPRINT 0: Foundation
# ═══════════════════════════════════════════════════════════════
class HealthCheckTests(TestCase):
    def test_health_endpoint(self):
        resp = self.client.get("/api/v1/health/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_openapi_schema(self):
        resp = self.client.get("/api/schema/")
        self.assertEqual(resp.status_code, 200)


# ═══════════════════════════════════════════════════════════════
# SPRINT 1: Auth, Profile, Onboarding
# ═══════════════════════════════════════════════════════════════
class AuthTests(TestCase):
    def test_signup_returns_tokens(self):
        resp = self.client.post("/api/v1/auth/signup/", {
            "username": "newuser", "email": "new@test.com", "password": "securepass1"
        }, content_type="application/json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("access", resp.json())
        self.assertIn("refresh", resp.json())
        self.assertEqual(resp.json()["user"]["username"], "newuser")

    def test_login_with_username(self):
        User.objects.create_user(username="logintest", email="lt@test.com", password="pass1234!")
        resp = self.client.post("/api/v1/auth/login/", {
            "username_or_email": "logintest", "password": "pass1234!"
        }, content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.json())

    def test_login_with_email(self):
        User.objects.create_user(username="emailtest", email="email@test.com", password="pass1234!")
        resp = self.client.post("/api/v1/auth/login/", {
            "username_or_email": "email@test.com", "password": "pass1234!"
        }, content_type="application/json")
        self.assertEqual(resp.status_code, 200)

    def test_login_invalid_credentials(self):
        resp = self.client.post("/api/v1/auth/login/", {
            "username_or_email": "nobody", "password": "wrong"
        }, content_type="application/json")
        self.assertEqual(resp.status_code, 400)

    def test_profile_auto_created_on_signup(self):
        user = User.objects.create_user(username="auto", email="auto@test.com", password="pass1234!")
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, UserProfile)


class ProfileTests(TestCase):
    def setUp(self):
        self.user = make_user("profuser")
        self.client = get_auth_client(self.user)

    def test_get_profile(self):
        resp = self.client.get("/api/v1/users/me/profile/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["diet_type"], "omnivore")

    def test_update_profile(self):
        resp = self.client.put("/api/v1/users/me/profile/", {
            "diet_type": "vegan", "health_conditions": ["diabetic"],
            "allergies": ["peanuts"], "disliked_ingredients": [],
            "preferred_cuisines": [], "calorie_target": 1800,
            "protein_target_g": 80, "carbs_target_g": 200,
            "fat_target_g": 60, "max_cooking_time_min": 30,
            "spice_tolerance": 2, "onboarding_completed": True,
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["diet_type"], "vegan")

    def test_dashboard_summary(self):
        resp = self.client.get("/api/v1/users/dashboard/summary/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("stats", data)
        self.assertIn("saved_recipes_count", data["stats"])


class SaveRecipeTests(TestCase):
    def setUp(self):
        self.user = make_user("saver")
        self.client = get_auth_client(self.user)
        self.recipe = make_recipe("Saveable Soup")

    def test_save_recipe(self):
        resp = self.client.post(f"/api/v1/recipes/{self.recipe.id}/save/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["created"])

    def test_save_idempotent(self):
        self.client.post(f"/api/v1/recipes/{self.recipe.id}/save/")
        resp = self.client.post(f"/api/v1/recipes/{self.recipe.id}/save/")
        self.assertFalse(resp.json()["created"])

    def test_list_saved(self):
        self.client.post(f"/api/v1/recipes/{self.recipe.id}/save/")
        resp = self.client.get("/api/v1/recipes/saved/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)


# ═══════════════════════════════════════════════════════════════
# SPRINT 2: Query Normalization, Parsing, Search
# ═══════════════════════════════════════════════════════════════
class NormalizerTests(TestCase):
    def test_typo_correction(self):
        result = normalize_query("vegitarian protien dinner")
        self.assertIn("vegetarian", result)
        self.assertIn("protein", result)

    def test_lowcarb_expansion(self):
        result = normalize_query("lowcarb meal")
        self.assertIn("low carb", result)

    def test_fuzzy_ingredient(self):
        result = normalize_query("chickn with tomatoe")
        self.assertIn("chicken", result)
        self.assertIn("tomato", result)


class ParserTests(TestCase):
    def test_diet_extraction(self):
        filters = parse_filters("vegan breakfast")
        self.assertEqual(filters["diet_type"], "vegan")
        self.assertEqual(filters["meal_type"], "breakfast")

    def test_time_extraction(self):
        filters = parse_filters("quick meal under 20 minutes")
        self.assertEqual(filters["max_time_min"], 20)

    def test_calorie_extraction(self):
        filters = parse_filters("meal under 500 calories")
        self.assertEqual(filters["max_calories"], 500)


class SearchAPITests(TestCase):
    def setUp(self):
        self.user = make_user("searcher")
        self.client = get_auth_client(self.user)
        make_recipe("Veggie Bowl", category="dinner", is_vegetarian=True, ingredients="spinach, tomato, onion")
        make_recipe("Chicken Stir Fry", category="dinner", is_vegetarian=False, ingredients="chicken, garlic, pepper")

    def test_search_returns_results(self):
        resp = self.client.post("/api/v1/search/", {"query": "vegetarian dinner"}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("results", data)
        self.assertGreater(len(data["results"]), 0)
        self.assertIn("search_log_id", data)

    def test_search_creates_log(self):
        self.client.post("/api/v1/search/", {"query": "spicy lunch"}, format="json")
        self.assertEqual(SearchLog.objects.filter(user=self.user).count(), 1)

    def test_search_with_typos(self):
        resp = self.client.post("/api/v1/search/", {"query": "vegitarian dinnr with spinch"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(len(resp.json()["results"]), 0)

    def test_search_empty_query_fails(self):
        resp = self.client.post("/api/v1/search/", {"query": ""}, format="json")
        self.assertEqual(resp.status_code, 400)


# ═══════════════════════════════════════════════════════════════
# SPRINT 3: Personalized Ranking & Explanations
# ═══════════════════════════════════════════════════════════════
class RankingTests(TestCase):
    def setUp(self):
        self.vegan_user = make_user("vegan_r", diet="vegan")
        self.omni_user = make_user("omni_r", diet="omnivore")
        self.veg_recipe = make_recipe("Lentil Bowl", is_vegetarian=True, ingredients="lentil, tomato")
        self.meat_recipe = make_recipe("Chicken Chili", is_vegetarian=False, ingredients="chicken, chili")

    def test_different_profiles_different_order(self):
        vegan_ranked, _ = rank_recipes(
            [self.veg_recipe, self.meat_recipe],
            user_profile=self.vegan_user.profile, query="dinner",
        )
        omni_ranked, _ = rank_recipes(
            [self.veg_recipe, self.meat_recipe],
            user_profile=self.omni_user.profile, query="chicken chili dinner",
        )
        self.assertEqual(vegan_ranked[0]["recipe"].id, self.veg_recipe.id)
        self.assertEqual(omni_ranked[0]["recipe"].id, self.meat_recipe.id)

    def test_ranking_includes_score_and_explanation(self):
        ranked, _ = rank_recipes(
            [self.veg_recipe], user_profile=self.vegan_user.profile, query="lentil",
        )
        self.assertIn("score", ranked[0])
        self.assertIn("explanation", ranked[0])
        self.assertIn("why", ranked[0]["explanation"])

    def test_popularity_boosts_liked_recipes(self):
        UserRecipeInteraction.objects.create(
            user=self.omni_user, recipe=self.meat_recipe, interaction_type="liked",
        )
        ranked, _ = rank_recipes(
            [self.veg_recipe, self.meat_recipe],
            user_profile=self.omni_user.profile, query="dinner",
        )
        scores = {r["recipe"].id: r["score"] for r in ranked}
        self.assertGreater(scores[self.meat_recipe.id], 0)


class ExplanationTests(TestCase):
    def test_explanation_captures_diet_match(self):
        user = make_user("explain_u", diet="vegetarian")
        recipe = make_recipe("Veggie Curry", is_vegetarian=True, protein=25, cooking_time=20)
        builder = ExplanationBuilder()
        result = builder.build(recipe, user.profile, breakdown={}, query_ingredients=[])
        self.assertIn("vegetarian", result["why"])


# ═══════════════════════════════════════════════════════════════
# SPRINT 4: Safety Engine
# ═══════════════════════════════════════════════════════════════
class SafetyRuleTests(TestCase):
    def setUp(self):
        self.user = make_user("safe_u", allergies=["peanuts"], conditions=["diabetic"])
        self.safe_recipe = make_recipe("Safe Salad", ingredients="lettuce, tomato", carbs=20, is_vegetarian=True)
        self.peanut_recipe = make_recipe("Peanut Stir Fry", ingredients="peanuts, soy sauce, tofu")
        self.high_carb = make_recipe("Pasta Feast", ingredients="pasta, cream", carbs=80)

    def test_allergy_blocked(self):
        warnings = evaluate_recipe_safety(self.peanut_recipe, self.user.profile)
        danger = [w for w in warnings if w["severity"] == "danger"]
        self.assertGreater(len(danger), 0)
        self.assertTrue(any("peanuts" in w["message"].lower() for w in danger))

    def test_safe_recipe_no_danger(self):
        warnings = evaluate_recipe_safety(self.safe_recipe, self.user.profile)
        danger = [w for w in warnings if w["severity"] == "danger"]
        self.assertEqual(len(danger), 0)

    def test_diabetic_high_carb_warning(self):
        warnings = evaluate_recipe_safety(self.high_carb, self.user.profile)
        carb_warnings = [w for w in warnings if "carb" in w["message"].lower()]
        self.assertGreater(len(carb_warnings), 0)

    def test_filter_dangerous_removes_allergen(self):
        safe, blocked = filter_dangerous_recipes(
            [self.safe_recipe, self.peanut_recipe], self.user.profile
        )
        safe_ids = [r.id for r, _ in safe]
        blocked_ids = [b["recipe_id"] for b in blocked]
        self.assertIn(self.safe_recipe.id, safe_ids)
        self.assertIn(self.peanut_recipe.id, blocked_ids)

    def test_vegan_blocks_non_veg(self):
        vegan = make_user("vegan_s", diet="vegan")
        meat = make_recipe("Beef Stew", ingredients="beef, potato", is_vegetarian=False)
        warnings = evaluate_recipe_safety(meat, vegan.profile)
        danger = [w for w in warnings if w["severity"] == "danger"]
        self.assertGreater(len(danger), 0)


class SafetyDBRuleTests(TestCase):
    def setUp(self):
        SafetyRule.objects.create(
            key="test_peanut_allergy", rule_type="allergen_contains",
            condition={"allergen": "peanuts"}, severity="danger",
            message_template="Contains {allergen} — dangerous for your allergy.",
        )
        self.user = make_user("dbr_u", allergies=["peanuts"])
        self.recipe = make_recipe("PB Sandwich", ingredients="peanut butter, bread")

    def test_db_rule_triggers(self):
        warnings = evaluate_recipe_safety(self.recipe, self.user.profile)
        self.assertTrue(any(w["rule_key"] == "test_peanut_allergy" for w in warnings))


class SafetyAPITests(TestCase):
    def setUp(self):
        self.user = make_user("safe_api_u", allergies=["peanuts"])
        self.client = get_auth_client(self.user)
        self.recipe = make_recipe("Peanut Dish", ingredients="peanuts, oil")

    def test_check_recipe_endpoint(self):
        resp = self.client.get(f"/api/v1/warnings/check/{self.recipe.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)
        self.assertGreater(len(resp.json()), 0)


# ═══════════════════════════════════════════════════════════════
# SPRINT 5: Meal Planner
# ═══════════════════════════════════════════════════════════════
class MealPlannerTests(TestCase):
    def setUp(self):
        self.user = make_user("planner_u", calorie_target=2000)
        make_recipe("Oatmeal", category="breakfast", calories=300, is_vegetarian=True)
        make_recipe("Grilled Chicken", category="lunch", calories=500)
        make_recipe("Pasta Dinner", category="dinner", calories=600)
        make_recipe("Fruit Snack", category="snack", calories=150, is_vegetarian=True)

    def test_generate_plan(self):
        plan = generate_meal_plan(self.user, date=datetime.date.today())
        self.assertIsInstance(plan, MealPlan)
        self.assertEqual(plan.user, self.user)
        self.assertGreater(plan.items.count(), 0)
        self.assertGreater(plan.total_calories, 0)

    def test_plan_replaces_existing(self):
        generate_meal_plan(self.user, date=datetime.date.today())
        generate_meal_plan(self.user, date=datetime.date.today())
        self.assertEqual(MealPlan.objects.filter(user=self.user, date=datetime.date.today()).count(), 1)

    def test_regenerate_item(self):
        plan = generate_meal_plan(self.user, date=datetime.date.today())
        item = plan.items.first()
        if item:
            old_recipe_id = item.recipe_id
            new_item = regenerate_meal_item(plan, item.id)
            # May or may not change recipe (small pool), but should not crash
            self.assertIsNotNone(new_item)

    def test_shopping_list(self):
        plan = generate_meal_plan(self.user, date=datetime.date.today())
        items = generate_shopping_list(plan)
        self.assertIsInstance(items, list)
        if items:
            self.assertIn("ingredient", items[0])
            self.assertIn("servings", items[0])

    def test_3_meal_plan(self):
        plan = generate_meal_plan(self.user, date=datetime.date.today(), num_meals=3)
        # Should not include snack
        meal_types = set(plan.items.values_list("meal_type", flat=True))
        self.assertNotIn("snack", meal_types)

    def test_workout_day_type(self):
        plan = generate_meal_plan(self.user, date=datetime.date.today(), day_type="workout")
        self.assertEqual(plan.day_type, "workout")


class MealPlanAPITests(TestCase):
    def setUp(self):
        self.user = make_user("plan_api_u", calorie_target=2000)
        self.client = get_auth_client(self.user)
        make_recipe("Morning Oats", category="breakfast", calories=300, is_vegetarian=True)
        make_recipe("Lunch Bowl", category="lunch", calories=500)
        make_recipe("Evening Rice", category="dinner", calories=600)
        make_recipe("Trail Mix", category="snack", calories=200, is_vegetarian=True)

    def test_generate_plan_api(self):
        resp = self.client.post("/api/v1/meal-plans/generate/", {
            "date": str(datetime.date.today()), "day_type": "normal", "num_meals": 4,
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertIn("total_calories", data)

    def test_get_plan_by_date(self):
        self.client.post("/api/v1/meal-plans/generate/", {
            "date": str(datetime.date.today()), "day_type": "normal", "num_meals": 4,
        }, format="json")
        resp = self.client.get(f"/api/v1/meal-plans/{datetime.date.today()}/")
        self.assertEqual(resp.status_code, 200)

    def test_shopping_list_api(self):
        resp = self.client.post("/api/v1/meal-plans/generate/", {
            "date": str(datetime.date.today()),
        }, format="json")
        plan_id = resp.json()["id"]
        resp = self.client.get(f"/api/v1/meal-plans/{plan_id}/shopping-list/")
        self.assertEqual(resp.status_code, 200)


# ═══════════════════════════════════════════════════════════════
# CROSS-CUTTING: Feedback, Recipe Detail, Legacy Endpoints
# ═══════════════════════════════════════════════════════════════
class FeedbackTests(TestCase):
    def setUp(self):
        self.user = make_user("fb_u")
        self.client = get_auth_client(self.user)
        self.recipe = make_recipe("Feedback Dish")

    def test_like_recipe(self):
        resp = self.client.post(f"/api/v1/recipes/{self.recipe.id}/feedback/", {
            "interaction_type": "liked", "rating": 5,
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(UserRecipeInteraction.objects.filter(
            user=self.user, recipe=self.recipe, interaction_type="liked"
        ).exists())

    def test_dislike_recipe(self):
        resp = self.client.post(f"/api/v1/recipes/{self.recipe.id}/feedback/", {
            "interaction_type": "disliked",
        }, format="json")
        self.assertEqual(resp.status_code, 200)


class RecipeDetailAPITests(TestCase):
    def setUp(self):
        self.recipe = make_recipe("Detail Recipe", ingredients="tomato, basil, mozzarella")

    def test_recipe_detail_v1(self):
        resp = self.client.get(f"/api/v1/recipes/{self.recipe.id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["name"], "Detail Recipe")
        self.assertIn("ingredients", data)

    def test_legacy_recipe_detail(self):
        resp = self.client.get(f"/recipe_detail/{self.recipe.id}/")
        self.assertEqual(resp.status_code, 200)


class LegacySearchTests(TestCase):
    def setUp(self):
        make_recipe("Onion Soup", ingredients="onion, garlic, broth", category="dinner", is_vegetarian=True)

    def test_legacy_get_recipes(self):
        resp = self.client.get("/get_recipes/", {"query": "onion dinner"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("recipes", resp.json())

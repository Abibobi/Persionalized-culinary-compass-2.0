from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserRecipeInteraction
from recipes.models import Recipe
from recommendations.services.explanations import ExplanationBuilder
from recommendations.services.ranking import rank_recipes


class RankingBehaviorTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user_vegan = User.objects.create_user(
			username="vegan_user",
			email="vegan@example.com",
			password="pass1234",
		)
		self.user_omni = User.objects.create_user(
			username="omni_user",
			email="omni@example.com",
			password="pass1234",
		)

		vegan_profile = self.user_vegan.profile
		vegan_profile.diet_type = "vegan"
		vegan_profile.save()

		omni_profile = self.user_omni.profile
		omni_profile.diet_type = "omnivore"
		omni_profile.save()

		self.recipe_veg = Recipe.objects.create(
			name="Lentil Bowl",
			description="Hearty plant-based dinner",
			ingredients="lentil, tomato, onion",
			category="dinner",
			protein=24,
			carbs=45,
			fat=10,
			fiber=9,
			vitamins={},
			calories=480,
			cooking_time=25,
			spicy_level=2,
			is_vegetarian=True,
		)
		self.recipe_meat = Recipe.objects.create(
			name="Chicken Chili",
			description="Spicy protein-rich chili",
			ingredients="chicken, tomato, chili",
			category="dinner",
			protein=32,
			carbs=20,
			fat=12,
			fiber=5,
			vitamins={},
			calories=520,
			cooking_time=35,
			spicy_level=4,
			is_vegetarian=False,
		)

		UserRecipeInteraction.objects.create(
			user=self.user_omni,
			recipe=self.recipe_meat,
			interaction_type="liked",
		)

	def test_profiles_produce_different_rankings(self):
		vegan_ranked, _ = rank_recipes(
			[self.recipe_veg, self.recipe_meat],
			user_profile=self.user_vegan.profile,
			query="chicken chili dinner",
		)
		omni_ranked, _ = rank_recipes(
			[self.recipe_veg, self.recipe_meat],
			user_profile=self.user_omni.profile,
			query="chicken chili dinner",
		)

		vegan_ids = [item["recipe"].id for item in vegan_ranked]
		omni_ids = [item["recipe"].id for item in omni_ranked]

		self.assertNotEqual(vegan_ids, omni_ids)
		self.assertEqual(vegan_ids[0], self.recipe_veg.id)
		self.assertEqual(omni_ids[0], self.recipe_meat.id)


class ExplanationBuilderTests(TestCase):
	def test_explanation_includes_core_reasons(self):
		User = get_user_model()
		user = User.objects.create_user(
			username="explainer",
			email="explain@example.com",
			password="pass1234",
		)

		profile = user.profile
		profile.diet_type = "vegetarian"
		profile.max_cooking_time_min = 30
		profile.save()

		recipe = Recipe.objects.create(
			name="Veggie Curry",
			description="A fast vegetarian curry",
			ingredients="tomato, onion, chickpea",
			category="dinner",
			protein=25,
			carbs=35,
			fat=9,
			fiber=8,
			vitamins={},
			calories=420,
			cooking_time=20,
			spicy_level=3,
			is_vegetarian=True,
		)

		builder = ExplanationBuilder()
		explanation = builder.build(recipe, profile, breakdown={}, query_ingredients=[])
		why = explanation["why"]

		self.assertIn("matches your vegetarian diet", why)
		self.assertIn("under 30 min prep", why)
		self.assertIn("high protein (25g)", why)

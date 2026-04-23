from django.test import TestCase
from django.core.management import call_command
from django.urls import reverse
from pathlib import Path
import tempfile
from unittest.mock import patch

from .models import Recipe
from . import views


class RecipeViewsTests(TestCase):
    def setUp(self):
        Recipe.objects.create(
            name="Veg Onion Stir Fry",
            description="Simple onion-based dish",
            ingredients="onion, garlic, pepper",
            category="dinner",
            protein=15.0,
            carbs=22.0,
            fat=10.0,
            fiber=4.0,
            vitamins={"vitamin c": 12},
            calories=280,
            cooking_time=25,
            spicy_level=3,
            instructions="Cook all ingredients.",
            is_vegetarian=True,
        )

    def test_get_recipes_returns_matches(self):
        response = self.client.get(reverse("get_recipes"), {"query": "vegetarian onion dinner"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("recipes", payload)
        self.assertEqual(len(payload["recipes"]), 1)
        self.assertEqual(payload["recipes"][0]["name"], "Veg Onion Stir Fry")


class ImportRecipesCommandTests(TestCase):
    def _write_csv(self, content):
        temp_dir = Path(tempfile.mkdtemp())
        csv_file = temp_dir / "recipes.csv"
        csv_file.write_text(content, encoding="utf-8")
        return str(csv_file)

    def test_import_recipes_parses_json_vitamins_and_boolean(self):
        csv_path = self._write_csv(
            "name,description,ingredients,category,protein,carbs,fat,fiber,vitamins,calories,cooking_time,spicy_level,instructions,is_vegetarian\n"
            "Recipe A,Desc,\"onion, garlic\",dinner,20,30,10,5,\"{\"\"vitamin c\"\": 8}\",450,35,3,Step by step,TRUE\n"
        )

        call_command("import_recipes", csv_path)

        recipe = Recipe.objects.get(name="Recipe A")
        self.assertEqual(recipe.vitamins, {"vitamin c": 8})
        self.assertTrue(recipe.is_vegetarian)

    def test_import_recipes_skips_invalid_row(self):
        csv_path = self._write_csv(
            "name,description,ingredients,category,protein,carbs,fat,fiber,vitamins,calories,cooking_time,spicy_level,instructions,is_vegetarian\n"
            "Bad Recipe,Desc,\"onion, garlic\",dinner,invalid,30,10,5,\"{\"\"vitamin c\"\": 8}\",450,35,3,Step by step,TRUE\n"
        )

        call_command("import_recipes", csv_path)

        self.assertEqual(Recipe.objects.count(), 0)

    def test_import_recipes_skips_non_object_vitamins_json(self):
        csv_path = self._write_csv(
            "name,description,ingredients,category,protein,carbs,fat,fiber,vitamins,calories,cooking_time,spicy_level,instructions,is_vegetarian\n"
            "Bad Vitamins,Desc,\"onion, garlic\",dinner,20,30,10,5,\"[]\",450,35,3,Step by step,TRUE\n"
        )

        call_command("import_recipes", csv_path)

        self.assertEqual(Recipe.objects.count(), 0)


class ViewsFallbackTests(TestCase):
    def test_load_nlp_falls_back_to_blank_model(self):
        with patch("recipes.views.spacy.load", side_effect=OSError):
            nlp_model = views._load_nlp()
        self.assertEqual(nlp_model.lang, "en")

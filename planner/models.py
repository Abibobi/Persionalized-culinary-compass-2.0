from django.conf import settings
from django.db import models


class MealPlan(models.Model):
	DAY_TYPES = [
		("normal", "Normal"),
		("workout", "Workout"),
		("low_carb", "Low Carb"),
	]

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="meal_plans",
	)
	date = models.DateField()
	day_type = models.CharField(max_length=20, choices=DAY_TYPES, default="normal")
	num_meals = models.IntegerField(default=4)
	target_calories = models.IntegerField(null=True, blank=True)

	total_calories = models.IntegerField(default=0)
	total_protein_g = models.FloatField(default=0)
	total_carbs_g = models.FloatField(default=0)
	total_fat_g = models.FloatField(default=0)
	warnings = models.JSONField(default=list, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "date")
		ordering = ["-date"]

	def recalculate_totals(self):
		totals = {
			"calories": 0,
			"protein": 0.0,
			"carbs": 0.0,
			"fat": 0.0,
		}
		for item in self.items.all():
			totals["calories"] += int(item.calories or 0)
			totals["protein"] += float(item.protein_g or 0)
			totals["carbs"] += float(item.carbs_g or 0)
			totals["fat"] += float(item.fat_g or 0)

		self.total_calories = totals["calories"]
		self.total_protein_g = round(totals["protein"], 1)
		self.total_carbs_g = round(totals["carbs"], 1)
		self.total_fat_g = round(totals["fat"], 1)
		self.save(update_fields=[
			"total_calories",
			"total_protein_g",
			"total_carbs_g",
			"total_fat_g",
		])

	def __str__(self):
		return f"{self.user.username} plan {self.date}"


class MealPlanItem(models.Model):
	MEAL_TYPES = [
		("breakfast", "Breakfast"),
		("lunch", "Lunch"),
		("dinner", "Dinner"),
		("snack", "Snack"),
	]

	meal_plan = models.ForeignKey(
		MealPlan,
		on_delete=models.CASCADE,
		related_name="items",
	)
	meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
	recipe = models.ForeignKey(
		"recipes.Recipe",
		on_delete=models.CASCADE,
		related_name="meal_plan_items",
	)
	servings = models.FloatField(default=1)

	calories = models.FloatField(default=0)
	protein_g = models.FloatField(default=0)
	carbs_g = models.FloatField(default=0)
	fat_g = models.FloatField(default=0)

	class Meta:
		ordering = ["meal_type"]

	def snapshot_nutrition(self):
		multiplier = max(float(self.servings or 0), 0)
		self.calories = round((self.recipe.calories or 0) * multiplier, 1)
		self.protein_g = round((self.recipe.protein or 0) * multiplier, 1)
		self.carbs_g = round((self.recipe.carbs or 0) * multiplier, 1)
		self.fat_g = round((self.recipe.fat or 0) * multiplier, 1)

	def __str__(self):
		return f"{self.meal_type}: {self.recipe.name}"

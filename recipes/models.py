from django.db import models

class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    category = models.CharField(max_length=50)  # e.g., breakfast, lunch, etc.
    protein = models.FloatField()  # grams
    carbs = models.FloatField()  # grams
    fat = models.FloatField()  # grams
    fiber = models.FloatField()  # grams
    vitamins = models.JSONField()  # e.g., {"vitamin A": 5, "vitamin C": 10}
    calories = models.IntegerField()  # calories per serving
    cooking_time = models.IntegerField()  # time in minutes
    spicy_level = models.IntegerField()  # scale of 1 to 5
    instructions = models.TextField(null=True, blank=True)
    is_vegetarian = models.BooleanField(default=False)  # whether the recipe is vegetarian

    def __str__(self):
        return self.name

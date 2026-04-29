from rest_framework import serializers
from .models import MealPlan, MealPlanItem


class MealPlanItemSerializer(serializers.ModelSerializer):
    recipe_name = serializers.CharField(source="recipe.name", read_only=True)

    class Meta:
        model = MealPlanItem
        fields = (
            "id", "meal_type", "recipe", "recipe_name",
            "servings", "calories", "protein_g", "carbs_g", "fat_g",
        )
        read_only_fields = ("calories", "protein_g", "carbs_g", "fat_g")


class MealPlanSerializer(serializers.ModelSerializer):
    items = MealPlanItemSerializer(many=True, read_only=True)

    class Meta:
        model = MealPlan
        fields = (
            "id", "date", "day_type", "num_meals", "target_calories",
            "total_calories", "total_protein_g", "total_carbs_g", "total_fat_g",
            "warnings", "created_at", "items",
        )
        read_only_fields = (
            "total_calories", "total_protein_g", "total_carbs_g",
            "total_fat_g", "warnings", "created_at",
        )


class GeneratePlanSerializer(serializers.Serializer):
    date = serializers.DateField(required=False)
    day_type = serializers.ChoiceField(
        choices=["normal", "workout", "low_carb"], default="normal",
    )
    num_meals = serializers.ChoiceField(choices=[3, 4], default=4)


class ShoppingItemSerializer(serializers.Serializer):
    ingredient = serializers.CharField()
    servings = serializers.FloatField()

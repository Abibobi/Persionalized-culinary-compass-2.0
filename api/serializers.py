from rest_framework import serializers
from recipes.models import Recipe


class SearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)


class RecipeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "description",
            "ingredients",
            "instructions",
            "category",
            "protein",
            "carbs",
            "fat",
            "fiber",
            "vitamins",
            "calories",
            "cooking_time",
            "spicy_level",
            "is_vegetarian",
        )


class FeedbackSerializer(serializers.Serializer):
    interaction_type = serializers.ChoiceField(choices=["liked", "disliked", "cooked"])
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False)
    note = serializers.CharField(max_length=500, required=False, allow_blank=True)

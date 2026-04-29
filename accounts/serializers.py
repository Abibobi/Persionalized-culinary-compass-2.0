from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserProfile, UserRecipeInteraction
from recipes.models import Recipe

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class UserProfileSerializer(serializers.ModelSerializer):
    health_conditions = serializers.ListField(child=serializers.CharField(), required=False)
    allergies = serializers.ListField(child=serializers.CharField(), required=False)
    disliked_ingredients = serializers.ListField(child=serializers.CharField(), required=False)
    preferred_cuisines = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = UserProfile
        fields = (
            "diet_type",
            "health_conditions",
            "allergies",
            "disliked_ingredients",
            "preferred_cuisines",
            "calorie_target",
            "protein_target_g",
            "carbs_target_g",
            "fat_target_g",
            "max_cooking_time_min",
            "spice_tolerance",
            "onboarding_completed",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

class OnboardingSerializer(serializers.ModelSerializer):
    health_conditions = serializers.ListField(child=serializers.CharField(), required=False)
    allergies = serializers.ListField(child=serializers.CharField(), required=False)
    disliked_ingredients = serializers.ListField(child=serializers.CharField(), required=False)
    preferred_cuisines = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = UserProfile
        fields = (
            "diet_type",
            "health_conditions",
            "allergies",
            "disliked_ingredients",
            "preferred_cuisines",
            "calorie_target",
            "protein_target_g",
            "carbs_target_g",
            "fat_target_g",
            "max_cooking_time_min",
            "spice_tolerance",
            "onboarding_completed",
        )

class SaveRecipeSerializer(serializers.Serializer):
    recipe_id = serializers.IntegerField()


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name")


class UserRecipeInteractionSerializer(serializers.ModelSerializer):
    recipe = RecipeMiniSerializer(read_only=True)

    class Meta:
        model = UserRecipeInteraction
        fields = ("id", "interaction_type", "rating", "note", "created_at", "recipe")
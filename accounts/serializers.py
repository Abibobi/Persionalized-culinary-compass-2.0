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
        fields = (
            "id",
            "name",
            "category",
            "calories",
            "protein",
            "carbs",
            "fat",
            "cooking_time",
            "spicy_level",
            "is_vegetarian",
        )


class UserRecipeInteractionSerializer(serializers.ModelSerializer):
    recipe = RecipeMiniSerializer(read_only=True)

    class Meta:
        model = UserRecipeInteraction
        fields = ("id", "interaction_type", "rating", "note", "created_at", "recipe")


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AuthTokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = MeSerializer()
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserProfile

User = get_user_model()


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class UserProfileSerializer(serializers.ModelSerializer):
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
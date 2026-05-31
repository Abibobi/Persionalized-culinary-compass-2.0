"""
Management command to seed demo users with diverse profiles.
Usage: python manage.py seed_demo_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from accounts.models import UserProfile
from safety.models import SafetyRule

User = get_user_model()

DEMO_USERS = [
    {
        "username": "demo_vegan",
        "email": "vegan@demo.com",
        "password": "demo1234!",
        "profile": {
            "diet_type": "vegan",
            "health_conditions": [],
            "allergies": ["peanuts", "soy"],
            "disliked_ingredients": ["mushrooms"],
            "preferred_cuisines": ["breakfast", "lunch"],
            "calorie_target": 1800,
            "protein_target_g": 80,
            "carbs_target_g": 200,
            "fat_target_g": 60,
            "max_cooking_time_min": 30,
            "spice_tolerance": 3,
            "onboarding_completed": True,
        },
    },
    {
        "username": "demo_diabetic",
        "email": "diabetic@demo.com",
        "password": "demo1234!",
        "profile": {
            "diet_type": "omnivore",
            "health_conditions": ["diabetic"],
            "allergies": ["shellfish"],
            "disliked_ingredients": [],
            "preferred_cuisines": ["dinner", "lunch"],
            "calorie_target": 2000,
            "protein_target_g": 120,
            "carbs_target_g": 150,
            "fat_target_g": 70,
            "max_cooking_time_min": 45,
            "spice_tolerance": 4,
            "onboarding_completed": True,
        },
    },
    {
        "username": "demo_athlete",
        "email": "athlete@demo.com",
        "password": "demo1234!",
        "profile": {
            "diet_type": "omnivore",
            "health_conditions": [],
            "allergies": [],
            "disliked_ingredients": ["bitter gourd"],
            "preferred_cuisines": ["breakfast", "dinner"],
            "calorie_target": 3000,
            "protein_target_g": 180,
            "carbs_target_g": 300,
            "fat_target_g": 100,
            "max_cooking_time_min": 60,
            "spice_tolerance": 5,
            "onboarding_completed": True,
        },
    },
]


class Command(BaseCommand):
    help = "Seed demo users with diverse profiles for portfolio showcasing"

    def handle(self, *args, **options):
        for user_data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={"email": user_data["email"]},
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
            else:
                self.stdout.write(f"User already exists: {user.username}")

            profile, _ = UserProfile.objects.get_or_create(user=user)
            for field, value in user_data["profile"].items():
                setattr(profile, field, value)
            profile.save()
            self.stdout.write(f"  Profile updated for {user.username}")

        self.stdout.write(self.style.SUCCESS("\nDemo users seeded successfully!"))
        self.stdout.write("Login credentials:")
        for u in DEMO_USERS:
            self.stdout.write(f"  {u['username']} / {u['password']}")

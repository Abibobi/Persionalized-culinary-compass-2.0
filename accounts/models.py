from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    DIET_CHOICES = [
        ("omnivore", "Omnivore"),
        ("vegetarian", "Vegetarian"),
        ("vegan", "Vegan"),
        ("pescatarian", "Pescatarian"),
        ("other", "Other"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES, default="omnivore")
    health_conditions = models.JSONField(default=list, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    disliked_ingredients = models.JSONField(default=list, blank=True)
    preferred_cuisines = models.JSONField(default=list, blank=True)

    calorie_target = models.IntegerField(null=True, blank=True)
    protein_target_g = models.FloatField(null=True, blank=True)
    carbs_target_g = models.FloatField(null=True, blank=True)
    fat_target_g = models.FloatField(null=True, blank=True)

    max_cooking_time_min = models.IntegerField(null=True, blank=True)
    spice_tolerance = models.IntegerField(null=True, blank=True)  # 1-5
    onboarding_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} profile"
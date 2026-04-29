from django.contrib import admin
from .models import UserProfile, UserRecipeInteraction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "diet_type", "onboarding_completed", "updated_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("diet_type", "onboarding_completed")

@admin.register(UserRecipeInteraction)
class UserRecipeInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe", "interaction_type", "rating", "created_at")
    list_filter = ("interaction_type",)
    search_fields = ("user__username", "recipe__title")
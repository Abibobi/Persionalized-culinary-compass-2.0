from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "diet_type", "onboarding_completed", "updated_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("diet_type", "onboarding_completed")
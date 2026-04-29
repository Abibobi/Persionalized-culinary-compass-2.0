from django.urls import path
from .views import (
    me, my_profile, update_my_profile, onboarding_update, dashboard_summary,
    save_recipe, unsave_recipe, my_saved_recipes,
)

urlpatterns = [
    path("me/", me, name="me"),
    path("me/profile/", my_profile, name="my-profile"),
    path("me/profile/update/", update_my_profile, name="update-my-profile"),
    path("me/profile/onboarding/", onboarding_update, name="onboarding-update"),
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
    path("recipes/save/", save_recipe, name="save-recipe"),
    path("recipes/unsave/", unsave_recipe, name="unsave-recipe"),
    path("recipes/saved/", my_saved_recipes, name="my-saved-recipes"),
]
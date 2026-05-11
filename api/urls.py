from django.urls import path, include
from .views import (
    health_check,
    queue_ping,
    task_status,
    recipe_detail,
    recipe_save,
    recipe_feedback,
    saved_recipes,
)

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("tasks/ping/", queue_ping, name="queue-ping"),
    path("tasks/<str:task_id>/", task_status, name="task-status"),
    path("auth/", include("accounts.auth_urls")),
    path("users/", include("accounts.urls")),
    path("search/", include("recommendations.urls")),
    path("warnings/", include("safety.urls")),
    path("meal-plans/", include("planner.urls")),
    path("recipes/saved/", saved_recipes, name="recipes-saved"),
    path("recipes/<int:recipe_id>/", recipe_detail, name="recipe-detail"),
    path("recipes/<int:recipe_id>/save/", recipe_save, name="recipe-save"),
    path("recipes/<int:recipe_id>/feedback/", recipe_feedback, name="recipe-feedback"),
]
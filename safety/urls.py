from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_rules, name="safety-rules"),
    path("check/<int:recipe_id>/", views.check_recipe, name="safety-check"),
]

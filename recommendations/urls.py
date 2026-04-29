from django.urls import path
from .views import search_recipes

urlpatterns = [
    path("", search_recipes, name="search-recipes"),
]
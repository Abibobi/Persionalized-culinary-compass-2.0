from django.urls import path
from .views import search_recipes, recent_searches

urlpatterns = [
    path("", search_recipes, name="search-recipes"),
    path("history/", recent_searches, name="search-history"),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('get_recipes/', views.get_recipes, name='get_recipes'),
    path('recipe_detail/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('bot/chat/', views.chatbot_view, name='chatbot'),
]
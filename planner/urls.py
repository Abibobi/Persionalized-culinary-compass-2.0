from django.urls import path
from . import views

urlpatterns = [
    path("generate/", views.generate_plan, name="generate-plan"),
    path("<str:date>/", views.get_plan, name="get-plan"),
    path("<int:plan_id>/items/<int:item_id>/regenerate/", views.regenerate_item, name="regenerate-item"),
    path("<int:plan_id>/shopping-list/", views.shopping_list, name="shopping-list"),
]

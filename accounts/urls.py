from django.urls import path
from .views import me, my_profile, update_my_profile

urlpatterns = [
    path("me/", me, name="me"),
    path("me/profile/", my_profile, name="my-profile"),
    path("me/profile/update/", update_my_profile, name="update-my-profile"),
]
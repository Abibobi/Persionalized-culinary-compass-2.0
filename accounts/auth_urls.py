from django.urls import path

from .auth_views import signup_view, login_view, logout_view

urlpatterns = [
    path("signup/", signup_view, name="auth-signup"),
    path("login/", login_view, name="auth-login"),
    path("logout/", logout_view, name="auth-logout"),
]

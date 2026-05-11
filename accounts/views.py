from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from .models import UserRecipeInteraction
from .serializers import (
    MeSerializer,
    UserProfileSerializer,
    OnboardingSerializer,
    SaveRecipeSerializer,
    UserRecipeInteractionSerializer,
)

@extend_schema(tags=["Profile"], summary="Get current authenticated user")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = MeSerializer(request.user)
    return Response(serializer.data)


@extend_schema(tags=["Profile"], summary="Get or update current user's profile")
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    profile = request.user.profile
    if request.method == "PUT":
        serializer = UserProfileSerializer(profile, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)


@extend_schema(
    tags=["Profile"],
    summary="Update current user's profile",
    request=UserProfileSerializer,           
    responses={200: UserProfileSerializer},  
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_my_profile(request):
    profile = request.user.profile
    serializer = UserProfileSerializer(profile, data=request.data, partial=False)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@extend_schema(
    tags=["Profile"],
    summary="Complete/update onboarding data",
    request=OnboardingSerializer,           # 👈 Add this
    responses={200: OnboardingSerializer},  # 👈 Add this
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def onboarding_update(request):
    profile = request.user.profile
    serializer = OnboardingSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(onboarding_completed=True)
    return Response(serializer.data)


@extend_schema(tags=["Profile"], summary="Dashboard summary for current user")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    import datetime
    from recommendations.models import SearchLog
    from planner.models import MealPlan

    profile = request.user.profile
    saved_count = UserRecipeInteraction.objects.filter(
        user=request.user, interaction_type="saved"
    ).count()
    search_count = SearchLog.objects.filter(user=request.user).count()

    today = datetime.date.today()
    active_plan = MealPlan.objects.filter(user=request.user, date=today).first()

    return Response(
        {
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
            },
            "profile": {
                "diet_type": profile.diet_type,
                "onboarding_completed": profile.onboarding_completed,
                "calorie_target": profile.calorie_target,
                "max_cooking_time_min": profile.max_cooking_time_min,
                "allergies_count": len(profile.allergies or []),
                "health_conditions_count": len(profile.health_conditions or []),
            },
            "stats": {
                "saved_recipes_count": saved_count,
                "recent_searches_count": search_count,
                "active_meal_plan": active_plan.id if active_plan else None,
            },
        }
    )

@extend_schema(
    tags=["Profile"],
    summary="Save a recipe for current user",
    request=SaveRecipeSerializer,
    responses={200: dict},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_recipe(request):
    serializer = SaveRecipeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    recipe = get_object_or_404(Recipe, id=serializer.validated_data["recipe_id"])
    obj, created = UserRecipeInteraction.objects.get_or_create(
        user=request.user,
        recipe=recipe,
        interaction_type="saved",
    )

    return Response(
        {"status": "saved", "created": created, "interaction_id": obj.id},
        status=200,
    )


@extend_schema(
    tags=["Profile"],
    summary="Remove saved recipe for current user",
    request=SaveRecipeSerializer,
    responses={200: dict},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unsave_recipe(request):
    serializer = SaveRecipeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    deleted_count, _ = UserRecipeInteraction.objects.filter(
        user=request.user,
        recipe_id=serializer.validated_data["recipe_id"],
        interaction_type="saved",
    ).delete()

    return Response({"status": "removed", "deleted": deleted_count})


@extend_schema(
    tags=["Profile"],
    summary="List saved recipes for current user",
    responses={200: UserRecipeInteractionSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_saved_recipes(request):
    qs = (
        UserRecipeInteraction.objects
        .filter(user=request.user, interaction_type="saved")
        .select_related("recipe")
        .order_by("-created_at")
    )
    data = UserRecipeInteractionSerializer(qs, many=True).data
    return Response(data)
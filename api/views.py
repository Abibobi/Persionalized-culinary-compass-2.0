from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from celery.result import AsyncResult
from django.shortcuts import get_object_or_404

from .tasks import ping_task
from .serializers import RecipeDetailSerializer, FeedbackSerializer
from accounts.models import UserRecipeInteraction
from accounts.serializers import UserRecipeInteractionSerializer
from recipes.models import Recipe


@extend_schema(tags=["Health"], summary="Health check")
@api_view(["GET"])
def health_check(request):
    return Response({"status": "ok", "service": "pcc-api", "version": "v1"})


@extend_schema(tags=["Health"], summary="Queue async ping task")
@api_view(["POST"])
def queue_ping(request):
    name = request.data.get("name", "chef")
    task = ping_task.delay(name)
    return Response({"task_id": task.id, "status": "queued"}, status=202)


@extend_schema(tags=["Health"], summary="Get async task status/result")
@api_view(["GET"])
def task_status(request, task_id):
    task_result = AsyncResult(task_id)
    payload = {
        "task_id": task_id,
        "state": task_result.state,
    }
    if task_result.ready():
        payload["result"] = task_result.result
    return Response(payload)


@extend_schema(tags=["Recipes"], summary="Get recipe detail", responses={200: RecipeDetailSerializer})
@api_view(["GET"])
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    return Response(RecipeDetailSerializer(recipe).data)


@extend_schema(tags=["Recipes"], summary="Save a recipe", responses={200: dict})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recipe_save(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    obj, created = UserRecipeInteraction.objects.get_or_create(
        user=request.user,
        recipe=recipe,
        interaction_type="saved",
    )
    return Response({"status": "saved", "created": created, "interaction_id": obj.id})


@extend_schema(
    tags=["Recipes"],
    summary="Leave recipe feedback",
    request=FeedbackSerializer,
    responses={200: dict},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def recipe_feedback(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    serializer = FeedbackSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    obj, created = UserRecipeInteraction.objects.update_or_create(
        user=request.user,
        recipe=recipe,
        interaction_type=serializer.validated_data["interaction_type"],
        defaults={
            "rating": serializer.validated_data.get("rating"),
            "note": serializer.validated_data.get("note", ""),
        },
    )

    return Response({"status": "recorded", "created": created, "interaction_id": obj.id})


@extend_schema(tags=["Recipes"], summary="List saved recipes", responses={200: UserRecipeInteractionSerializer(many=True)})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saved_recipes(request):
    qs = (
        UserRecipeInteraction.objects
        .filter(user=request.user, interaction_type="saved")
        .select_related("recipe")
        .order_by("-created_at")
    )
    return Response(UserRecipeInteractionSerializer(qs, many=True).data)
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Recipe

from .models import SafetyRule
from .serializers import SafetyRuleSerializer, RecipeWarningSerializer
from .services.rules_engine import evaluate_recipe_safety


@extend_schema(
	tags=["Safety"],
	summary="List active safety rules",
	responses={200: SafetyRuleSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_rules(request):
	qs = SafetyRule.objects.filter(is_active=True).order_by("severity", "key")
	return Response(SafetyRuleSerializer(qs, many=True).data)


@extend_schema(
	tags=["Safety"],
	summary="Evaluate safety warnings for a recipe",
	responses={200: RecipeWarningSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_recipe(request, recipe_id):
	recipe = get_object_or_404(Recipe, id=recipe_id)
	warnings = evaluate_recipe_safety(recipe, request.user.profile)
	return Response(warnings)

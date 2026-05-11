import datetime

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MealPlan
from .serializers import (
	GeneratePlanSerializer,
	MealPlanSerializer,
	MealPlanItemSerializer,
	ShoppingItemSerializer,
)
from .services.day_planner import (
	generate_meal_plan,
	regenerate_meal_item,
	generate_shopping_list,
)


@extend_schema(
	tags=["Meal Plans"],
	summary="Generate a daily meal plan",
	request=GeneratePlanSerializer,
	responses={200: MealPlanSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_plan(request):
	serializer = GeneratePlanSerializer(data=request.data)
	serializer.is_valid(raise_exception=True)

	plan = generate_meal_plan(
		request.user,
		date=serializer.validated_data.get("date"),
		day_type=serializer.validated_data.get("day_type", "normal"),
		num_meals=serializer.validated_data.get("num_meals", 4),
	)
	return Response(MealPlanSerializer(plan).data)


@extend_schema(
	tags=["Meal Plans"],
	summary="Get meal plan by date",
	responses={200: MealPlanSerializer},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_plan(request, date):
	try:
		parsed_date = datetime.date.fromisoformat(date)
	except ValueError:
		return Response({"detail": "Invalid date format. Use YYYY-MM-DD."}, status=400)
	plan = get_object_or_404(MealPlan, user=request.user, date=parsed_date)
	return Response(MealPlanSerializer(plan).data)


@extend_schema(
	tags=["Meal Plans"],
	summary="Regenerate a single meal item",
	responses={200: MealPlanItemSerializer},
)
@api_view(["PATCH", "POST"])
@permission_classes([IsAuthenticated])
def regenerate_item(request, plan_id, item_id):
	plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
	item = regenerate_meal_item(plan, item_id)
	if item is None:
		return Response({"detail": "Unable to regenerate meal item."}, status=400)
	return Response(MealPlanItemSerializer(item).data)


@extend_schema(
	tags=["Meal Plans"],
	summary="Get shopping list for plan",
	responses={200: ShoppingItemSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def shopping_list(request, plan_id):
	plan = get_object_or_404(MealPlan, id=plan_id, user=request.user)
	items = generate_shopping_list(plan)
	return Response(items)

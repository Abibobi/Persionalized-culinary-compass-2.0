import time
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services.normalizer import normalize_query
from .services.parser import parse_filters
from recipes.models import Recipe
from .serializers import SearchRequestSerializer, SearchResponseSerializer, RecipeSearchResultSerializer
from .services.ranking import score_recipe

from .models import SearchLog
from .serializers import (
    SearchRequestSerializer,
    SearchResponseSerializer,
)


@extend_schema(
    tags=["Search"],
    summary="Search recipes (skeleton)",
    request=SearchRequestSerializer,
    responses={200: SearchResponseSerializer},
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def search_recipes(request):
    start = time.perf_counter()

    req = SearchRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)

    raw_query = req.validated_data["query"]
    normalized_query = normalize_query(raw_query)
    parsed_filters = parse_filters(normalized_query)
    
    qs = Recipe.objects.all()

    # diet_type → map to is_vegetarian
    diet = parsed_filters.get("diet_type")
    if diet in {"vegetarian", "vegan"}:
        qs = qs.filter(is_vegetarian=True)

    # meal_type → category
    if parsed_filters.get("meal_type"):
        qs = qs.filter(category__iexact=parsed_filters["meal_type"])

    # max_time_min → cooking_time
    if parsed_filters.get("max_time_min"):
        qs = qs.filter(cooking_time__lte=parsed_filters["max_time_min"])

    # max_calories → calories
    if parsed_filters.get("max_calories"):
        qs = qs.filter(calories__lte=parsed_filters["max_calories"])

    qs = qs[:20]
    recipes = list(qs)
    recipes.sort(key=score_recipe, reverse=True)
    
    warnings = []

    # TODO Phase 3: allergy cross-check + nutrition risk
    results = RecipeSearchResultSerializer(recipes, many=True).data
    result_count = len(results)


    latency_ms = int((time.perf_counter() - start) * 1000)

    search_log = SearchLog.objects.create(
        user=request.user,
        raw_query=raw_query,
        normalized_query=normalized_query,
        parsed_filters=parsed_filters,
        result_count=len(results),
        latency_ms=latency_ms,
    )

    response = {
        "search_log_id": search_log.id,
        "normalized_query": normalized_query,
        "parsed_filters": parsed_filters,
        "results": results,
        "warnings": [],
    }

    return Response(response)
import time
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services.normalizer import normalize_query
from .services.parser import parse_filters
from .services.gemini_fallback import gemini_recipe_suggestions
from recipes.models import Recipe
from .models import SearchLog
from .serializers import SearchRequestSerializer, SearchResponseSerializer, RecipeSearchResultSerializer
from .services.ranking import rank_recipes
from .services.search_logger import log_search


@extend_schema(
    tags=["Search"],
    summary="Search recipes with hybrid retrieval and safety-aware ranking",
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

    recipes = list(qs)

    ranked, _blocked = rank_recipes(
        recipes,
        parsed_filters=parsed_filters,
        user_profile=request.user.profile,
        query=normalized_query,
    )

    results = []
    warnings = []

    for entry in ranked[:20]:
        recipe = entry["recipe"]
        recipe_data = RecipeSearchResultSerializer(recipe).data
        recipe_data["score"] = entry["score"]
        recipe_data["explanation"] = entry["explanation"]
        results.append(recipe_data)

        if entry["warnings"]:
            warnings.append({"recipe_id": recipe.id, "warnings": entry["warnings"]})

    # Gemini fallback when no results
    ai_suggestions = None
    if not results:
        ai_data = gemini_recipe_suggestions(
            raw_query,
            user_profile=request.user.profile,
        )
        if ai_data.get("recipes"):
            ai_suggestions = ai_data

    latency_ms = int((time.perf_counter() - start) * 1000)

    search_log = log_search(
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
        "warnings": warnings,
    }
    if ai_suggestions:
        response["ai_suggestions"] = ai_suggestions

    return Response(response)


@extend_schema(
    tags=["Search"],
    summary="Get recent search history for current user",
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recent_searches(request):
    from .serializers import SearchLogSerializer
    logs = SearchLog.objects.filter(user=request.user).order_by("-created_at")[:10]
    return Response(SearchLogSerializer(logs, many=True).data)

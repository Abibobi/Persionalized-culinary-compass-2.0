import time
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services.normalizer import normalize_query


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
    parsed_filters = {}
    

    # TODO (Phase 2+): real parser + retrieval + ranking
    results = []

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
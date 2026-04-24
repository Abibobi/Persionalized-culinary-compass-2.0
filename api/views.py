from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response


@extend_schema(
    tags=["Health"],
    summary="Health check",
    description="Returns API service health status.",
)
@api_view(["GET"])
def health_check(request):
    return Response({
        "status": "ok",
        "service": "pcc-api",
        "version": "v1",
    })
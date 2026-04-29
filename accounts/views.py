from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import MeSerializer, UserProfileSerializer


@extend_schema(tags=["Profile"], summary="Get current authenticated user")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = MeSerializer(request.user)
    return Response(serializer.data)


@extend_schema(tags=["Profile"], summary="Get current user's profile")
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    profile = request.user.profile
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)


@extend_schema(
    tags=["Profile"],
    summary="Update current user's profile",
    request=UserProfileSerializer,           # 👈 This is what's missing
    responses={200: UserProfileSerializer},  # 👈 Good to add this too
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_my_profile(request):
    profile = request.user.profile
    serializer = UserProfileSerializer(profile, data=request.data, partial=False)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupSerializer, LoginSerializer, MeSerializer, AuthTokenSerializer

User = get_user_model()


@extend_schema(
    tags=["Auth"],
    summary="Sign up user",
    request=SignupSerializer,
    responses={201: AuthTokenSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    payload = _token_payload(user)
    return Response(payload, status=201)


@extend_schema(
    tags=["Auth"],
    summary="Login user with username or email",
    request=LoginSerializer,
    responses={200: AuthTokenSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username_or_email = serializer.validated_data["username_or_email"].strip()
    password = serializer.validated_data["password"]

    candidate_username = username_or_email
    if "@" in username_or_email:
        user_obj = User.objects.filter(email__iexact=username_or_email).first()
        candidate_username = user_obj.username if user_obj else username_or_email

    user = authenticate(request=request, username=candidate_username, password=password)
    if user is None:
        return Response({"detail": "Invalid credentials."}, status=400)

    payload = _token_payload(user)
    return Response(payload)


@extend_schema(tags=["Auth"], summary="Logout user")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    return Response({"status": "logged_out"})


def _token_payload(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": MeSerializer(user).data,
    }

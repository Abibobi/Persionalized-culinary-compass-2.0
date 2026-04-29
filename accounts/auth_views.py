from django.contrib.auth import authenticate, login, logout, get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import SignupSerializer, LoginSerializer, MeSerializer

User = get_user_model()


@extend_schema(
    tags=["Auth"],
    summary="Sign up user",
    request=SignupSerializer,
    responses={201: MeSerializer},
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return Response(MeSerializer(user).data, status=201)


@extend_schema(
    tags=["Auth"],
    summary="Login user with username or email",
    request=LoginSerializer,
    responses={200: MeSerializer},
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

    login(request, user)
    return Response(MeSerializer(user).data)


@extend_schema(tags=["Auth"], summary="Logout user")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"status": "logged_out"})

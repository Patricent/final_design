from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import UserProfile
from .serializers import RegisterSerializer, UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        profile = getattr(user, "profile", None)
        token["nickname"] = (profile.nickname if profile else "") or ""
        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user, context={"request": request}).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        UserProfile.objects.get_or_create(user=request.user)
        return Response(UserSerializer(request.user, context={"request": request}).data)

    def patch(self, request):
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = request.data
        if "nickname" in data:
            profile.nickname = data.get("nickname") or ""
        if "bio" in data:
            profile.bio = data.get("bio") or ""
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]
        profile.save()
        if "email" in data:
            user.email = data.get("email") or ""
            user.save(update_fields=["email"])
        return Response(UserSerializer(user, context={"request": request}).data)


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]

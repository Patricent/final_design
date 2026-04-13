from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .crypto_keys import encrypt_secret
from .models import UserProfile
from .serializers import RegisterSerializer, UserApiKeysUpdateSerializer, UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["is_staff"] = user.is_staff
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
        user = User.objects.select_related("profile").get(pk=request.user.pk)
        return Response(UserSerializer(user, context={"request": request}).data)

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
        user = User.objects.select_related("profile").get(pk=user.pk)
        return Response(UserSerializer(user, context={"request": request}).data)


class UserApiKeysView(APIView):
    """保存用户自有的大模型 API Key（加密存储）；未配置时使用系统环境变量中的默认 Key。"""

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        UserProfile.objects.get_or_create(user=request.user)
        profile = request.user.profile
        ser = UserApiKeysUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        updates = [
            ("qwen_clear", "qwen_api_key", "api_key_qwen_enc"),
            ("deepseek_clear", "deepseek_api_key", "api_key_deepseek_enc"),
            ("gpt_clear", "gpt_api_key", "api_key_openai_enc"),
        ]
        for clear_flag, key_field, enc_attr in updates:
            if d.get(clear_flag):
                setattr(profile, enc_attr, "")
                continue
            val = (d.get(key_field) or "").strip()
            if val:
                setattr(profile, enc_attr, encrypt_secret(val))

        profile.save()
        user = User.objects.select_related("profile").get(pk=request.user.pk)
        return Response(UserSerializer(user, context={"request": request}).data)


class ChangePasswordView(APIView):
    """已登录用户修改密码：需校验当前密码。"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get("old_password") or ""
        new_password = request.data.get("new_password") or ""
        new_password_confirm = request.data.get("new_password_confirm") or ""
        user = request.user

        if not user.check_password(old_password):
            return Response(
                {"old_password": ["当前密码不正确"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_password != new_password_confirm:
            return Response(
                {"new_password_confirm": ["两次输入的新密码不一致"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if old_password == new_password:
            return Response(
                {"new_password": ["新密码不能与当前密码相同"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            validate_password(new_password, user=user)
        except ValidationError as exc:
            return Response({"new_password": list(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"detail": "密码已更新，请使用新密码重新登录"})


class RefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]

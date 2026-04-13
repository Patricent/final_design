from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "email", "nickname", "avatar")
        read_only_fields = ("id", "username")

    def get_nickname(self, obj):
        p = getattr(obj, "profile", None)
        return p.nickname if p else ""

    def get_avatar(self, obj):
        p = getattr(obj, "profile", None)
        if not p or not p.avatar:
            return None
        request = self.context.get("request")
        url = p.avatar.url
        return request.build_absolute_uri(url) if request else url


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被注册")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "两次输入的密码不一致"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        nickname = validated_data.pop("nickname", "") or ""
        password = validated_data.pop("password")
        email = validated_data.get("email") or ""
        user = User.objects.create_user(
            username=validated_data["username"],
            email=email,
            password=password,
        )
        UserProfile.objects.create(user=user, nickname=nickname)
        return user

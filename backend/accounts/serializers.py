from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    has_qwen_api_key = serializers.SerializerMethodField()
    has_deepseek_api_key = serializers.SerializerMethodField()
    has_gpt_api_key = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "nickname",
            "avatar",
            "bio",
            "is_staff",
            "has_qwen_api_key",
            "has_deepseek_api_key",
            "has_gpt_api_key",
        )
        read_only_fields = (
            "id",
            "username",
            "is_staff",
            "has_qwen_api_key",
            "has_deepseek_api_key",
            "has_gpt_api_key",
        )

    def get_nickname(self, obj):
        p = getattr(obj, "profile", None)
        return p.nickname if p else ""

    def get_bio(self, obj):
        p = getattr(obj, "profile", None)
        return p.bio if p else ""

    def get_avatar(self, obj):
        p = getattr(obj, "profile", None)
        if not p or not p.avatar:
            return None
        request = self.context.get("request")
        url = p.avatar.url
        return request.build_absolute_uri(url) if request else url

    def get_has_qwen_api_key(self, obj):
        p = UserProfile.objects.filter(user=obj).first()
        return bool(p and p.api_key_qwen_enc)

    def get_has_deepseek_api_key(self, obj):
        p = UserProfile.objects.filter(user=obj).first()
        return bool(p and p.api_key_deepseek_enc)

    def get_has_gpt_api_key(self, obj):
        p = UserProfile.objects.filter(user=obj).first()
        return bool(p and p.api_key_openai_enc)


class UserApiKeysUpdateSerializer(serializers.Serializer):
    """更新 LLM API Key：勾选 clear 则清除；否则非空字符串为覆盖；未传则不修改。"""

    qwen_api_key = serializers.CharField(required=False, allow_blank=True, max_length=2048)
    qwen_clear = serializers.BooleanField(required=False, default=False)
    deepseek_api_key = serializers.CharField(required=False, allow_blank=True, max_length=2048)
    deepseek_clear = serializers.BooleanField(required=False, default=False)
    gpt_api_key = serializers.CharField(required=False, allow_blank=True, max_length=2048)
    gpt_clear = serializers.BooleanField(required=False, default=False)


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

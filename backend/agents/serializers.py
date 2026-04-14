from rest_framework import serializers

from integrations.volcengine_cv_client import REQ_KEY_T2I_V30

from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "kind",
            "description",
            "model_key",
            "temperature",
            "is_public",
            "image_width",
            "image_height",
            "owner_id",
            "owner_username",
        ]
        read_only_fields = ["id", "owner_id", "owner_username"]

    def validate(self, attrs):
        kind = attrs.get("kind")
        if self.instance:
            kind = kind if kind is not None else self.instance.kind
        else:
            kind = kind or Agent.KIND_CHAT
        if kind == Agent.KIND_IMAGE:
            attrs["kind"] = Agent.KIND_IMAGE
            if not attrs.get("model_key"):
                attrs["model_key"] = REQ_KEY_T2I_V30
            w = attrs.get("image_width")
            if w is None and self.instance:
                w = self.instance.image_width
            if w is None:
                w = 1328
            h = attrs.get("image_height")
            if h is None and self.instance:
                h = self.instance.image_height
            if h is None:
                h = 1328
            w, h = int(w), int(h)
            if not (512 <= w <= 2048 and 512 <= h <= 2048):
                raise serializers.ValidationError({"image_width": "宽高需在 512–2048 之间"})
            attrs["image_width"] = w
            attrs["image_height"] = h
        else:
            attrs["kind"] = Agent.KIND_CHAT
        return attrs

    def get_owner_username(self, obj):
        if obj.owner_id and obj.owner:
            return obj.owner.username
        return ""


class AgentAdminSerializer(serializers.ModelSerializer):
    """管理员列表：含删除、公开状态与时间字段。"""

    owner_username = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "kind",
            "description",
            "model_key",
            "temperature",
            "is_public",
            "image_width",
            "image_height",
            "is_deleted",
            "deleted_at",
            "owner_id",
            "owner_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_owner_username(self, obj):
        if obj.owner_id and obj.owner:
            return obj.owner.username
        return ""

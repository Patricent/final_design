from rest_framework import serializers

from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    owner_username = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "description",
            "model_key",
            "temperature",
            "is_public",
            "owner_id",
            "owner_username",
        ]
        read_only_fields = ["id", "owner_id", "owner_username"]

    def get_owner_username(self, obj):
        if obj.owner_id and obj.owner:
            return obj.owner.username
        return ""

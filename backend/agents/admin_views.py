from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Agent
from .permissions import IsAdminUser
from .serializers import AgentAdminSerializer


class AdminAgentAllListView(APIView):
    """管理员：所有未软删除的智能体。"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        agents = (
            Agent.objects.filter(is_deleted=False)
            .select_related("owner")
            .order_by("-updated_at")
        )
        return Response(AgentAdminSerializer(agents, many=True).data)


class AdminAgentRecycleListView(APIView):
    """管理员：回收站（仅已软删除）。"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        agents = (
            Agent.objects.filter(is_deleted=True)
            .select_related("owner")
            .order_by("-deleted_at", "-updated_at")
        )
        return Response(AgentAdminSerializer(agents, many=True).data)


class AdminAgentUnpublishView(APIView):
    """广场下架：is_public -> False（不软删除）。"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        agent = get_object_or_404(Agent, pk=pk, is_deleted=False)
        agent.is_public = False
        agent.save(update_fields=["is_public", "updated_at"])
        return Response(AgentAdminSerializer(agent).data)


class AdminAgentSoftDeleteView(APIView):
    """软删除：标记 is_deleted，并自动下架。"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        agent = get_object_or_404(Agent, pk=pk, is_deleted=False)
        agent.is_deleted = True
        agent.deleted_at = timezone.now()
        agent.is_public = False
        agent.save(update_fields=["is_deleted", "deleted_at", "is_public", "updated_at"])
        return Response(AgentAdminSerializer(agent).data)


class AdminAgentRestoreView(APIView):
    """从回收站恢复（不自动恢复公开状态）。"""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        agent = get_object_or_404(Agent, pk=pk, is_deleted=True)
        agent.is_deleted = False
        agent.deleted_at = None
        agent.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        return Response(AgentAdminSerializer(agent).data)

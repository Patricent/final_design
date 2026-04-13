from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Agent
from .serializers import AgentSerializer


# 简单的模型列表（假数据），后续可从数据库或配置中读取
AVAILABLE_MODELS = [
    {
        "key": "qwen-plus",  # 与官方文档示例一致的模型名
        "label": "Qwen-Plus",
        "provider": "Qwen",
        "description": "通用中文/多语言大模型，适合复杂对话与创作。",
    },
    {
        "key": "deepseek-chat",
        "label": "DeepSeek-Chat",
        "provider": "DeepSeek",
        "description": "高性价比对话模型，推理能力较强。",
    },
    {
        "key": "gpt-4o-mini",
        "label": "GPT-4o-mini",
        "provider": "OpenAI",
        "description": "轻量级 GPT-4 体验，速度快、成本低。",
    },
]


class AgentView(APIView):
    """
    创建或更新一个智能体配置。
    简化实现：前端只需要一个当前正在编辑的 Agent。
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 兼容前端字段名：modelKey -> model_key、isPublic -> is_public
        incoming = request.data.copy()
        if "modelKey" in incoming and "model_key" not in incoming:
            incoming["model_key"] = incoming["modelKey"]
        if "isPublic" in incoming and "is_public" not in incoming:
            incoming["is_public"] = incoming["isPublic"]

        # 如果传了 id 就更新，否则创建
        agent_id = incoming.get("id")
        instance = None
        if agent_id:
            instance = Agent.objects.filter(pk=agent_id, owner=request.user).first()

        serializer = AgentSerializer(instance=instance, data=incoming)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentSquareListView(APIView):
    """
    智能体广场：所有用户公开的智能体。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        agents = (
            Agent.objects.filter(is_public=True)
            .select_related("owner")
            .order_by("-updated_at")
        )
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentListView(APIView):
    """
    返回当前登录用户拥有的智能体。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        agents = Agent.objects.filter(owner=request.user).order_by("-updated_at")
        serializer = AgentSerializer(agents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentDetailView(APIView):
    """
    返回单个智能体详情。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        agent = get_object_or_404(
            Agent.objects.filter(Q(owner=request.user) | Q(is_public=True)),
            pk=pk,
        )
        serializer = AgentSerializer(agent)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        agent = get_object_or_404(Agent, pk=pk, owner=request.user)
        agent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ModelListView(APIView):
    """
    返回可用大模型列表（当前为写死的假数据）。
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(AVAILABLE_MODELS)

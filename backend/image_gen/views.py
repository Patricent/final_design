from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from agents.models import Agent
from conversations.views import _agent_usable_by
from integrations.volcengine_cv_client import (
    get_text_to_image_result,
    submit_text_to_image_task,
)


class ImageGenSubmitView(APIView):
    """提交火山引擎文生图任务（通用 3.0）。"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        agent_id = request.data.get("agent_id")
        prompt = (request.data.get("prompt") or "").strip()
        if not agent_id:
            return Response({"detail": "agent_id 必填"}, status=status.HTTP_400_BAD_REQUEST)
        if not prompt:
            return Response({"detail": "prompt 不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(
            Agent.objects.filter(is_deleted=False, kind=Agent.KIND_IMAGE),
            pk=agent_id,
        )
        if not _agent_usable_by(request.user, agent):
            return Response({"detail": "无权使用该智能体"}, status=status.HTTP_403_FORBIDDEN)

        w = agent.image_width or 1328
        h = agent.image_height or 1328
        seed = request.data.get("seed", -1)
        scale = request.data.get("scale", 2.5)
        use_pre_llm = bool(request.data.get("use_pre_llm", False))
        try:
            seed = int(seed)
        except (TypeError, ValueError):
            seed = -1
        try:
            scale = float(scale)
        except (TypeError, ValueError):
            scale = 2.5

        try:
            task_id = submit_text_to_image_task(
                prompt,
                width=w,
                height=h,
                seed=seed,
                scale=scale,
                use_pre_llm=use_pre_llm,
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"task_id": task_id}, status=status.HTTP_200_OK)


class ImageGenResultView(APIView):
    """查询文生图任务结果。"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get("task_id")
        agent_id = request.data.get("agent_id")
        if not task_id:
            return Response({"detail": "task_id 必填"}, status=status.HTTP_400_BAD_REQUEST)
        if not agent_id:
            return Response({"detail": "agent_id 必填"}, status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(
            Agent.objects.filter(is_deleted=False, kind=Agent.KIND_IMAGE),
            pk=agent_id,
        )
        if not _agent_usable_by(request.user, agent):
            return Response({"detail": "无权使用该智能体"}, status=status.HTTP_403_FORBIDDEN)

        try:
            raw = get_text_to_image_result(str(task_id))
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        if raw.get("code") != 10000:
            return Response(
                {
                    "code": raw.get("code"),
                    "message": raw.get("message"),
                    "status": None,
                    "image_urls": [],
                },
                status=status.HTTP_200_OK,
            )

        data = raw.get("data") or {}
        return Response(
            {
                "code": 10000,
                "status": data.get("status"),
                "image_urls": data.get("image_urls") or [],
                "binary_data_base64": data.get("binary_data_base64"),
            },
            status=status.HTTP_200_OK,
        )

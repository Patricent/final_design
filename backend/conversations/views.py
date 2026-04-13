import time

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.jwt_utils import get_user_from_jwt_request
from accounts.user_llm_keys import (
    build_deepseek_client,
    build_openai_client,
    build_qwen_client,
)
from agents.models import Agent
from .models import Conversation, Message


def _agent_usable_by(user, agent: Agent) -> bool:
    if agent.is_deleted:
        return False
    return agent.owner_id == user.id or agent.is_public


def _conversation_agent_active(conversation) -> bool:
    return not conversation.agent.is_deleted


class ConversationCreateView(APIView):
    """
    创建一个新的会话。

    请求体示例：{"agent_id": 1}
    响应体示例：{"id": 1, "history": []}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        agent_id = request.data.get("agent_id")
        if not agent_id:
            return Response({"detail": "agent_id 是必填项"}, status=status.HTTP_400_BAD_REQUEST)

        agent = get_object_or_404(Agent.objects.filter(is_deleted=False), pk=agent_id)
        if not _agent_usable_by(request.user, agent):
            return Response({"detail": "无权使用该智能体"}, status=status.HTTP_403_FORBIDDEN)
        conv = Conversation.objects.create(agent=agent, started_by=request.user)

        data = {"id": conv.id, "history": []}
        return Response(data, status=status.HTTP_201_CREATED)


class MessageCreateView(APIView):
    """
    向指定会话追加一条用户消息。

    简化：这里只负责记录消息，并返回 stream_id，真正的回答由 /stream/ 接口模拟。

    请求体示例：{"content": "你好"}
    响应体示例：{"stream_id": 1}
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        conversation = get_object_or_404(Conversation, pk=pk, started_by=request.user)
        if not _conversation_agent_active(conversation):
            return Response(
                {"detail": "该智能体已不可用"},
                status=status.HTTP_403_FORBIDDEN,
            )

        content = request.data.get("content", "").strip()
        if not content:
            return Response({"detail": "content 不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        Message.objects.create(conversation=conversation, role="user", content=content)

        # 当前实现仅返回会话 id 作为 stream_id，前端随后会调用 /stream/
        return Response({"stream_id": conversation.id}, status=status.HTTP_200_OK)


class ConversationAbortView(APIView):
    """
    将会话标记为 aborted，流式接口会检测并停止输出。
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        conversation = get_object_or_404(Conversation, pk=pk, started_by=request.user)
        if not _conversation_agent_active(conversation):
            return Response(
                {"detail": "该智能体已不可用"},
                status=status.HTTP_403_FORBIDDEN,
            )
        conversation.aborted = True
        conversation.save(update_fields=["aborted"])
        return Response({"status": "aborted"}, status=status.HTTP_200_OK)


class ConversationStreamView(View):
    """
    使用 Server-Sent Events (SSE) 模拟流式回答。

    实际项目中，这里应当调用大模型的流式接口，将 chunk 逐步写入。
    目前为了演示，使用固定文本 + sleep 模拟。
    """

    def get(self, request, pk: int):
        user = get_user_from_jwt_request(request)
        if not user:
            return HttpResponse("Unauthorized", status=401)
        conversation = get_object_or_404(Conversation, pk=pk, started_by=user)
        if not _conversation_agent_active(conversation):
            return HttpResponse("Forbidden", status=403)
        agent = conversation.agent
        started_by = conversation.started_by

        def event_stream():
            # 取历史消息，主要用来构造提示词
            history = list(
                conversation.messages.order_by("created_at").values("role", "content")
            )

            model_key = (agent.model_key or "").strip()
            mk = model_key.lower()
            temp = agent.temperature or 0.7
            sys_prompt = agent.description or ""

            def stream_with_client(client, label: str):
                try:
                    for chunk in client.stream_chunks(
                        system_prompt=sys_prompt,
                        history=history,
                        model=model_key,
                        temperature=temp,
                    ):
                        conv = Conversation.objects.get(pk=conversation.pk)
                        if conv.aborted:
                            yield "data: [END]\n\n"
                            return
                        if chunk:
                            yield f"data: {chunk}\n\n"
                    yield "data: [END]\n\n"
                except Exception as exc:
                    yield f"data: **错误**：调用 {label} 失败：{exc}\n\n"
                    yield "data: [END]\n\n"

            if mk.startswith("qwen"):
                try:
                    client = build_qwen_client(started_by)
                except Exception as exc:
                    yield f"data: **错误**：{exc}\n\n"
                    yield "data: [END]\n\n"
                    return
                yield from stream_with_client(client, "Qwen")
                return

            if mk.startswith("deepseek"):
                try:
                    client = build_deepseek_client(started_by)
                except Exception as exc:
                    yield f"data: **错误**：{exc}\n\n"
                    yield "data: [END]\n\n"
                    return
                yield from stream_with_client(client, "DeepSeek")
                return

            if mk.startswith("gpt"):
                try:
                    client = build_openai_client(started_by)
                except Exception as exc:
                    yield f"data: **错误**：{exc}\n\n"
                    yield "data: [END]\n\n"
                    return
                yield from stream_with_client(client, "OpenAI")
                return

            # 默认本地假数据回答
            last_user_msg = conversation.messages.filter(role="user").order_by("-created_at").first()
            question = last_user_msg.content if last_user_msg else "（无问题）"

            fake_answer_parts = [
                "## 模拟回答（流式输出示例）\n\n",
                f"你刚才问的是：**{question}**。\n\n",
                "下面是一些 Markdown 示例内容：\n\n",
                "1. 支持列表\n",
                "2. **加粗文字**\n",
                "3. `行内代码`\n\n",
                "```python\n",
                "def hello():\n",
                "    print('Hello from fake stream')\n",
                "```\n\n",
                "以上为模拟数据，实际项目中会替换为真实大模型输出。\n",
            ]

            for chunk in fake_answer_parts:
                conv = Conversation.objects.get(pk=conversation.pk)
                if conv.aborted:
                    yield "data: [END]\n\n"
                    return

                yield f"data: {chunk}\n\n"
                time.sleep(0.3)

            yield "data: [END]\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response

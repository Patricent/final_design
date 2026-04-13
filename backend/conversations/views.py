import time

from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.jwt_utils import get_user_from_jwt_request
from agents.models import Agent
from integrations.llm_clients.qwen_client import QwenClient
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

        def event_stream():
            # 取历史消息，主要用来构造提示词
            history = list(
                conversation.messages.order_by("created_at").values("role", "content")
            )

            # 如果选择 Qwen 模型，则调用 Qwen 接口；否则回退到本地假数据
            model_key = (agent.model_key or "").strip()
            use_qwen = model_key.startswith("qwen")

            if use_qwen:
                client = QwenClient()
                try:
                    # 直接使用流式生成器，实时yield每个chunk
                    # 这样不会有内容丢失，也不需要等待完整回答
                    for chunk in client.stream_chunks(
                        system_prompt=agent.description or "",
                        history=history,
                        model=model_key,
                        temperature=agent.temperature or 0.7,
                    ):
                        # 检查是否被中止
                        conv = Conversation.objects.get(pk=conversation.pk)
                        if conv.aborted:
                            yield "data: [END]\n\n"
                            return
                        
                        # 实时发送每个chunk
                        if chunk:
                            yield f"data: {chunk}\n\n"
                    
                    # 流式输出完成
                    yield "data: [END]\n\n"
                    return
                        
                except Exception as exc:
                    # 调用失败时，将错误信息通过流返回给前端
                    error_msg = f"调用 Qwen 模型失败：{exc}"
                    yield f"data: **错误**：{error_msg}\n\n"
                    yield "data: [END]\n\n"
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

from django.conf import settings
from django.db import models

from agents.models import Agent


class Conversation(models.Model):
    """
    多轮对话会话。
    """

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="conversations")
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="started_conversations",
        verbose_name="发起用户",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    aborted = models.BooleanField(default=False)


class Message(models.Model):
    """
    会话中的一条消息。
    role: user / assistant
    """

    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

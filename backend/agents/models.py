from django.conf import settings
from django.db import models


class Agent(models.Model):
    """
    简单的智能体定义：用于保存角色名称、描述和所选模型等。
    每个智能体归属于创建者，仅本人可见与操作。
    """

    KIND_CHAT = "chat"
    KIND_IMAGE = "image"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="agents",
        verbose_name="所属用户",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, blank=True)
    kind = models.CharField(
        "类型",
        max_length=20,
        default=KIND_CHAT,
        db_index=True,
    )
    description = models.TextField(blank=True)
    model_key = models.CharField(max_length=100, blank=True)
    image_width = models.PositiveIntegerField("文生图宽度", null=True, blank=True)
    image_height = models.PositiveIntegerField("文生图高度", null=True, blank=True)
    temperature = models.FloatField(default=0.7)
    is_public = models.BooleanField("公开到广场", default=False)
    is_deleted = models.BooleanField("已删除", default=False, db_index=True)
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name or f"Agent#{self.pk}"

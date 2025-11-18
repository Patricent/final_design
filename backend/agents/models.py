from django.db import models


class Agent(models.Model):
  """
  简单的智能体定义：用于保存角色名称、描述和所选模型等。
  """

  name = models.CharField(max_length=100, blank=True)
  description = models.TextField(blank=True)
  model_key = models.CharField(max_length=100, blank=True)
  temperature = models.FloatField(default=0.7)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self) -> str:
      return self.name or f"Agent#{self.pk}"

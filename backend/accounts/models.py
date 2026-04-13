from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """扩展资料：昵称、头像、个人介绍（账号仍使用 Django 内置 User）。"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="用户")
    nickname = models.CharField("昵称", max_length=50, blank=True)
    avatar = models.ImageField("头像", upload_to="avatars/", blank=True, null=True)
    bio = models.TextField("个人介绍", blank=True)

    class Meta:
        db_table = "accounts_userprofile"
        verbose_name = "用户资料"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.nickname or self.user.username

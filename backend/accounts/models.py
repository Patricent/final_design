from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


class UserProfile(models.Model):
    """扩展资料：昵称、头像、个人介绍（账号仍使用 Django 内置 User）。"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="用户")
    nickname = models.CharField("昵称", max_length=50, blank=True)
    # 使用 FileField 而非 ImageField，避免 Django 启动时对 Pillow 的强制检查。
    # 若 backend 目录下误放 PIL.py 等，会遮蔽 site-packages 中的 Pillow，导致 ImageField 误报未安装。
    avatar = models.FileField(
        "头像",
        upload_to="avatars/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif", "webp", "jfif", "bmp"])
        ],
    )
    bio = models.TextField("个人介绍", blank=True)
    api_key_qwen_enc = models.TextField("Qwen API Key（加密）", blank=True, default="")
    api_key_deepseek_enc = models.TextField("DeepSeek API Key（加密）", blank=True, default="")
    api_key_openai_enc = models.TextField("OpenAI API Key（加密）", blank=True, default="")

    class Meta:
        db_table = "accounts_userprofile"
        verbose_name = "用户资料"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.nickname or self.user.username

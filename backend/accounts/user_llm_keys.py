"""根据发起对话的用户解析应使用的 LLM 客户端（自定义 Key 优先，否则环境变量）。"""

from __future__ import annotations

import os

from django.contrib.auth.models import User

from integrations.llm_clients.openai_compatible import OpenAICompatibleClient
from integrations.llm_clients.qwen_client import QwenClient

from .crypto_keys import decrypt_secret
from .models import UserProfile


def _profile_enc(user: User, attr: str) -> str:
    p = UserProfile.objects.filter(user=user).first()
    if not p:
        return ""
    return getattr(p, attr, "") or ""


def build_qwen_client(user: User) -> QwenClient:
    raw = _profile_enc(user, "api_key_qwen_enc")
    if raw:
        key = decrypt_secret(raw)
        if key:
            return QwenClient(api_key=key)
    return QwenClient()


def build_deepseek_client(user: User) -> OpenAICompatibleClient:
    raw = _profile_enc(user, "api_key_deepseek_enc")
    key = decrypt_secret(raw) if raw else ""
    key = key or os.getenv("DEEPSEEK_API_KEY") or ""
    if not key:
        raise RuntimeError("未配置 DeepSeek API Key（请在资料页填写或使用系统环境变量 DEEPSEEK_API_KEY）")
    base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1").rstrip("/")
    return OpenAICompatibleClient(api_key=key, base_url=base)


def build_openai_client(user: User) -> OpenAICompatibleClient:
    raw = _profile_enc(user, "api_key_openai_enc")
    key = decrypt_secret(raw) if raw else ""
    key = key or os.getenv("OPENAI_API_KEY") or ""
    if not key:
        raise RuntimeError("未配置 OpenAI API Key（请在资料页填写或使用系统环境变量 OPENAI_API_KEY）")
    base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").rstrip("/")
    return OpenAICompatibleClient(api_key=key, base_url=base)

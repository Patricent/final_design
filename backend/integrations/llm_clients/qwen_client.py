import os
from typing import Iterable, List, Dict, Any

import requests


class QwenClient:
    """
    Qwen 官方 API 封装（阿里云百炼 / DashScope 的 OpenAI 兼容协议）。

    - 优先使用环境变量 DASHSCOPE_API_KEY 作为鉴权密钥（形如 sk-xxxx），
      若未设置则回退到 QWEN_API_KEY。
    - 默认使用北京地域兼容模式地址：
      https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
    - 这里使用非流式请求，拿到完整回答后再在本地切片为小块，供前端流式展示。
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        # 官方示例使用 DASHSCOPE_API_KEY，这里同时兼容 QWEN_API_KEY
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise RuntimeError("未找到 DASHSCOPE_API_KEY 或 QWEN_API_KEY，请在 .env 或系统环境变量中设置。")
        # DashScope 兼容模式基础地址（北京地域），可通过 QWEN_API_BASE 覆盖
        self.base_url = base_url or os.getenv(
            "QWEN_API_BASE",
            "https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

    def _build_messages(self, system_prompt: str, history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        将系统提示词和历史对话转换为 OpenAI 兼容的 messages 结构。
        history: [{"role": "user" / "assistant", "content": "..."}, ...]
        """
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for item in history:
            role = item.get("role")
            content = item.get("content", "")
            if not content:
                continue
            # role 已经是 user / assistant
            messages.append({"role": role, "content": content})
        return messages

    def generate_text(
        self,
        system_prompt: str,
        history: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
    ) -> str:
        """
        调用 Qwen Chat Completions 接口，获取完整回答文本。
        """
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": self._build_messages(system_prompt, history),
            "temperature": temperature,
            "stream": False,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"Qwen 接口请求失败：{exc}") from exc

        try:
            data = resp.json()
        except Exception as exc:
            raise RuntimeError("Qwen 返回了无法解析的 JSON 响应") from exc

        # OpenAI 兼容格式：choices[0].message.content
        try:
            choices = data.get("choices") or []
            if not choices:
                raise RuntimeError(f"Qwen 响应中没有 choices 字段：{data}")
            message = choices[0].get("message") or {}
            content = message.get("content", "")
        except Exception as exc:
            raise RuntimeError(f"Qwen 响应解析失败：{data}") from exc

        if not content:
            raise RuntimeError("Qwen 返回内容为空，请检查模型名称、配额或请求参数。")

        return content

    def stream_chunks(
        self,
        system_prompt: str,
        history: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        chunk_size: int = 80,
    ) -> Iterable[str]:
        """
        伪流式接口：一次性向 Qwen 请求完整回答，然后在本地切成小段依次 yield。
        """
        full_text = self.generate_text(system_prompt, history, model=model, temperature=temperature)
        for i in range(0, len(full_text), chunk_size):
            yield full_text[i : i + chunk_size]




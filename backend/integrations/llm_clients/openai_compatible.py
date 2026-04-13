"""OpenAI 兼容协议流式调用（适用于 DeepSeek、OpenAI 等）。"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List

import requests


class OpenAICompatibleClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _build_messages(self, system_prompt: str, history: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for item in history:
            role = item.get("role")
            content = item.get("content", "")
            if not content:
                continue
            messages.append({"role": role, "content": content})
        return messages

    def stream_chunks(
        self,
        system_prompt: str,
        history: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
    ) -> Iterable[str]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": self._build_messages(system_prompt, history),
            "temperature": temperature,
            "stream": True,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=120, stream=True)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"LLM 接口请求失败：{exc}") from exc

        for line in resp.iter_lines():
            if not line:
                continue
            line_str = line.decode("utf-8")
            if not line_str.startswith("data: "):
                continue
            data_str = line_str[6:]
            if data_str.strip() == "[DONE]":
                break
            try:
                data = json.loads(data_str)
                choices = data.get("choices") or []
                if choices:
                    delta = choices[0].get("delta") or {}
                    content = delta.get("content", "")
                    if content:
                        yield content
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

"""
火山引擎视觉智能 CV接口（JSON + SignerV4），不依赖 volcengine SDK 的 Crypto 模块。
文档：visual.volcengineapi.com，Region=cn-north-1，Service=cv。
"""

from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import os
from collections import OrderedDict
from typing import Any, Dict
from urllib.parse import quote, urlencode

import requests

VISUAL_HOST = "visual.volcengineapi.com"
SERVICE = "cv"
REGION = "cn-north-1"
VERSION = "2022-08-31"
REQ_KEY_T2I_V30 = "high_aes_general_v30l_zt2i"


def _sha256_hex(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _hmac_sha256(key: bytes, content: str) -> bytes:
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


def _to_hex(digest: bytes) -> str:
    return "".join(f"{b:02x}" for b in digest)


def _norm_uri(path: str) -> str:
    return quote(path, safe="/~").replace("%2F", "/").replace("+", "%20")


def _norm_query(params: OrderedDict) -> str:
    parts = []
    for key in sorted(params.keys()):
        v = params[key]
        parts.append(
            quote(str(key), safe="-_.~") + "=" + quote(str(v), safe="-_.~")
        )
    return "&".join(parts).replace("+", "%20")


def _get_credentials():
    ak = os.getenv("VOLCENGINE_ACCESS_KEY_ID") or os.getenv("VOLC_ACCESSKEY") or ""
    sk = os.getenv("VOLCENGINE_SECRET_ACCESS_KEY") or os.getenv("VOLC_SECRETKEY") or ""
    if not ak or not sk:
        raise RuntimeError(
            "未配置火山引擎密钥：请在环境变量中设置 VOLCENGINE_ACCESS_KEY_ID 与 "
            "VOLCENGINE_SECRET_ACCESS_KEY（或 VOLC_ACCESSKEY / VOLC_SECRETKEY）"
        )
    return ak, sk


def _signing_key(sk: str, date: str, region: str, service: str) -> bytes:
    k_date = _hmac_sha256(sk.encode("utf-8"), date)
    k_region = _hmac_sha256(k_date, region)
    k_service = _hmac_sha256(k_region, service)
    return _hmac_sha256(k_service, "request")


def _sign_request(
    method: str,
    path: str,
    query: OrderedDict,
    body: str,
    host: str,
    ak: str,
    sk: str,
) -> Dict[str, str]:
    format_date = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    short_date = format_date[:8]
    body_hash = _sha256_hex(body)

    headers = OrderedDict(
        [
            ("Host", host.split(":")[0] if ":" in host else host),
            ("Content-Type", "application/json"),
            ("X-Date", format_date),
            ("X-Content-Sha256", body_hash),
        ]
    )

    signed_headers_dict = {}
    for key, val in headers.items():
        lk = key.lower()
        if lk in ("content-type", "content-md5", "host") or key.startswith("X-"):
            signed_headers_dict[lk] = val
    if "host" in signed_headers_dict and ":" in signed_headers_dict["host"]:
        h, _, port = signed_headers_dict["host"].partition(":")
        if port in ("80", "443"):
            signed_headers_dict["host"] = h

    signed_str = ""
    for key in sorted(signed_headers_dict.keys()):
        signed_str += key + ":" + signed_headers_dict[key] + "\n"
    signed_headers_keys = ";".join(sorted(signed_headers_dict.keys()))

    canonical = "\n".join(
        [
            method,
            _norm_uri(path),
            _norm_query(query),
            signed_str,
            signed_headers_keys,
            body_hash,
        ]
    )
    credential_scope = f"{short_date}/{REGION}/{SERVICE}/request"
    hashed_canon = _sha256_hex(canonical)
    signing_string = "\n".join(
        ["HMAC-SHA256", format_date, credential_scope, hashed_canon]
    )
    sk_sign = _signing_key(sk, short_date, REGION, SERVICE)
    signature = _to_hex(_hmac_sha256(sk_sign, signing_string))
    authorization = (
        f"HMAC-SHA256 Credential={ak}/{credential_scope}, "
        f"SignedHeaders={signed_headers_keys}, Signature={signature}"
    )
    out = {k: v for k, v in headers.items()}
    out["Authorization"] = authorization
    return out


def _post_cv(action: str, body_dict: Dict[str, Any]) -> Dict[str, Any]:
    ak, sk = _get_credentials()
    query = OrderedDict([("Action", action), ("Version", VERSION)])
    body = json.dumps(body_dict, ensure_ascii=False, separators=(",", ":"))
    path = "/"
    url = f"https://{VISUAL_HOST}{path}?{urlencode(query)}"
    headers = _sign_request("POST", path, query, body, VISUAL_HOST, ak, sk)
    resp = requests.post(
        url,
        data=body.encode("utf-8"),
        headers=dict(headers),
        timeout=120,
    )
    try:
        data = resp.json()
    except Exception as exc:
        raise RuntimeError(f"火山引擎返回非 JSON：HTTP {resp.status_code} {resp.text[:500]}") from exc
    if resp.status_code != 200:
        raise RuntimeError(
            data.get("message") or data.get("ResponseMetadata", {}).get("Error", {}).get("Message")
            or str(data)
        )
    return data


def submit_text_to_image_task(
    prompt: str,
    *,
    width: int = 1328,
    height: int = 1328,
    seed: int = -1,
    scale: float = 2.5,
    use_pre_llm: bool = False,
) -> str:
    """提交文生图任务，返回 task_id。"""
    prompt = (prompt or "").strip()
    if not prompt:
        raise ValueError("prompt 不能为空")
    body = {
        "req_key": REQ_KEY_T2I_V30,
        "prompt": prompt,
        "seed": seed,
        "width": int(width),
        "height": int(height),
        "scale": float(scale),
        "use_pre_llm": bool(use_pre_llm),
    }
    data = _post_cv("CVSync2AsyncSubmitTask", body)
    if data.get("code") != 10000:
        raise RuntimeError(data.get("message") or str(data))
    tid = (data.get("data") or {}).get("task_id")
    if not tid:
        raise RuntimeError(f"未返回 task_id：{data}")
    return str(tid)


def get_text_to_image_result(task_id: str) -> Dict[str, Any]:
    """查询任务完整响应体（含 code/message）；return_url 在 req_json 中开启。"""
    req_json = json.dumps({"return_url": True}, ensure_ascii=False, separators=(",", ":"))
    body = {
        "req_key": REQ_KEY_T2I_V30,
        "task_id": task_id,
        "req_json": req_json,
    }
    return _post_cv("CVSync2AsyncGetResult", body)

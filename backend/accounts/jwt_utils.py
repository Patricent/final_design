"""从 HTTP Authorization 或查询参数中解析 JWT，供 SSE 等非 DRF 视图使用。"""

from django.contrib.auth.models import User
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


def get_user_from_access_token_string(token: str):
    if not token:
        return None
    try:
        access = AccessToken(token)
        return User.objects.get(pk=access["user_id"])
    except (InvalidToken, TokenError, User.DoesNotExist, KeyError):
        return None


def get_user_from_jwt_request(request):
    token = None
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
    if not token:
        token = (request.GET.get("token") or "").strip()
    return get_user_from_access_token_string(token)

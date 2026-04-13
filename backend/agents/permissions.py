from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """仅 Django User.is_staff 为 True 的管理员可访问。"""

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.is_staff)

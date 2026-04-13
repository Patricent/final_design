from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    MeView,
    RefreshTokenView,
    RegisterView,
    UserApiKeysView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="auth-login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="auth-token-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("api-keys/", UserApiKeysView.as_view(), name="auth-api-keys"),
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
]

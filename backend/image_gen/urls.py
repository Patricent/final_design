from django.urls import path

from .views import ImageGenResultView, ImageGenSubmitView

urlpatterns = [
    path("submit/", ImageGenSubmitView.as_view(), name="image-gen-submit"),
    path("result/", ImageGenResultView.as_view(), name="image-gen-result"),
]

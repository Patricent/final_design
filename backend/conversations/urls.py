from django.urls import path

from .views import (
    ConversationCreateView,
    MessageCreateView,
    ConversationAbortView,
    ConversationStreamView,
)

urlpatterns = [
    path("", ConversationCreateView.as_view(), name="conversation-create"),
    path("<int:pk>/messages/", MessageCreateView.as_view(), name="message-create"),
    path("<int:pk>/abort/", ConversationAbortView.as_view(), name="conversation-abort"),
    path("<int:pk>/stream/", ConversationStreamView.as_view(), name="conversation-stream"),
]




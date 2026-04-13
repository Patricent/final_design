from django.urls import path

from .views import (
    AgentView,
    AgentListView,
    AgentSquareListView,
    AgentDetailView,
    ModelListView,
)

urlpatterns = [
    path("", AgentView.as_view(), name="agent-upsert"),
    path("list/", AgentListView.as_view(), name="agent-list"),
    path("square/", AgentSquareListView.as_view(), name="agent-square"),
    path("models/", ModelListView.as_view(), name="model-list"),
    path("<int:pk>/", AgentDetailView.as_view(), name="agent-detail"),
]




from django.urls import path

from .admin_views import (
    AdminAgentAllListView,
    AdminAgentRecycleListView,
    AdminAgentRestoreView,
    AdminAgentSoftDeleteView,
    AdminAgentUnpublishView,
)
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
    path("admin/all/", AdminAgentAllListView.as_view(), name="agent-admin-all"),
    path("admin/recycle/", AdminAgentRecycleListView.as_view(), name="agent-admin-recycle"),
    path(
        "admin/<int:pk>/unpublish/",
        AdminAgentUnpublishView.as_view(),
        name="agent-admin-unpublish",
    ),
    path(
        "admin/<int:pk>/soft-delete/",
        AdminAgentSoftDeleteView.as_view(),
        name="agent-admin-soft-delete",
    ),
    path(
        "admin/<int:pk>/restore/",
        AdminAgentRestoreView.as_view(),
        name="agent-admin-restore",
    ),
    path("models/", ModelListView.as_view(), name="model-list"),
    path("<int:pk>/", AgentDetailView.as_view(), name="agent-detail"),
]




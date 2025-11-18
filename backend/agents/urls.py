from django.urls import path

from .views import AgentView, ModelListView

urlpatterns = [
    path("", AgentView.as_view(), name="agent-upsert"),
    path("models/", ModelListView.as_view(), name="model-list"),
]




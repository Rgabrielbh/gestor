from django.urls import path
from .views_frontend import (
    NotebookListView, NotebookDetailView, NotebookCreateView,
    NotebookUpdateView, NotebookDeleteView, notebook_historico_json
)
urlpatterns = [
    path("", NotebookListView.as_view(), name="notebooks-list"),
    path("novo/", NotebookCreateView.as_view(), name="notebooks-create"),
    path("<int:pk>/", NotebookDetailView.as_view(), name="notebooks-detail"),
    path("<int:pk>/editar/", NotebookUpdateView.as_view(), name="notebooks-update"),
    path("<int:pk>/excluir/", NotebookDeleteView.as_view(), name="notebooks-delete"),
    path("<int:pk>/historico-json/", notebook_historico_json, name="notebooks-historico-json"),
]

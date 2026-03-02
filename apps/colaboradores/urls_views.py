from django.urls import path
from .views_frontend import ColaboradorListView, ColaboradorDetailView, ColaboradorCreateView, ColaboradorUpdateView, ColaboradorDeleteView

urlpatterns = [
    path("", ColaboradorListView.as_view(), name="colaboradores-list"),
    path("novo/", ColaboradorCreateView.as_view(), name="colaboradores-create"),
    path("<int:pk>/", ColaboradorDetailView.as_view(), name="colaboradores-detail"),
    path("<int:pk>/editar/", ColaboradorUpdateView.as_view(), name="colaboradores-update"),
    path("<int:pk>/excluir/", ColaboradorDeleteView.as_view(), name="colaboradores-delete"),
]

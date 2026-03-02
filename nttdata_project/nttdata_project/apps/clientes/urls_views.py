from django.urls import path
from .views_frontend import ClienteListView, ClienteDetailView, ClienteCreateView, ClienteUpdateView, ClienteDeleteView
urlpatterns = [
    path("", ClienteListView.as_view(), name="clientes-list"),
    path("novo/", ClienteCreateView.as_view(), name="clientes-create"),
    path("<int:pk>/", ClienteDetailView.as_view(), name="clientes-detail"),
    path("<int:pk>/editar/", ClienteUpdateView.as_view(), name="clientes-update"),
    path("<int:pk>/excluir/", ClienteDeleteView.as_view(), name="clientes-delete"),
]

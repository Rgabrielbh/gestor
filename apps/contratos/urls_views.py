from django.urls import path
from .views_frontend import ContratoListView, ContratoDetailView, ContratoCreateView, ContratoUpdateView, ContratoDeleteView
urlpatterns = [
    path("", ContratoListView.as_view(), name="contratos-list"),
    path("novo/", ContratoCreateView.as_view(), name="contratos-create"),
    path("<int:pk>/", ContratoDetailView.as_view(), name="contratos-detail"),
    path("<int:pk>/editar/", ContratoUpdateView.as_view(), name="contratos-update"),
    path("<int:pk>/excluir/", ContratoDeleteView.as_view(), name="contratos-delete"),
]

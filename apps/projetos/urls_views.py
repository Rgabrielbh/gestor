from django.urls import path
from .views_frontend import (ProjetoListView, ProjetoDetailView, ProjetoCreateView,
                              ProjetoUpdateView, ProjetoDeleteView, AlocacaoCreateView)
urlpatterns = [
    path("", ProjetoListView.as_view(), name="projetos-list"),
    path("novo/", ProjetoCreateView.as_view(), name="projetos-create"),
    path("<int:pk>/", ProjetoDetailView.as_view(), name="projetos-detail"),
    path("<int:pk>/editar/", ProjetoUpdateView.as_view(), name="projetos-update"),
    path("<int:pk>/excluir/", ProjetoDeleteView.as_view(), name="projetos-delete"),
    path("alocar/", AlocacaoCreateView.as_view(), name="alocacao-create"),
]

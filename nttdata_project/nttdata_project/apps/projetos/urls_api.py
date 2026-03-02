from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import ProjetoViewSet, GestorProjetoViewSet, ColaboradorProjetoViewSet

router = DefaultRouter()
router.register(r"projetos", ProjetoViewSet, basename="projeto")
router.register(r"gestores", GestorProjetoViewSet, basename="gestor-projeto")
router.register(r"alocacoes", ColaboradorProjetoViewSet, basename="alocacao")
urlpatterns = [path("", include(router.urls))]

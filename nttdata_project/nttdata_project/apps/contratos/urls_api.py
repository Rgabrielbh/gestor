from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import ContratoViewSet

router = DefaultRouter()
router.register(r"", ContratoViewSet, basename="contrato")
urlpatterns = [path("", include(router.urls))]

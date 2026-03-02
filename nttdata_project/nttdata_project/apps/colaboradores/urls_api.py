from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import ColaboradorViewSet

router = DefaultRouter()
router.register(r"", ColaboradorViewSet, basename="colaborador")
urlpatterns = [path("", include(router.urls))]

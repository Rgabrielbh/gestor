from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import ClienteViewSet

router = DefaultRouter()
router.register(r"", ClienteViewSet, basename="cliente")
urlpatterns = [path("", include(router.urls))]

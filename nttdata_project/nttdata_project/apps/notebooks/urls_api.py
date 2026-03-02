from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import NotebookViewSet

router = DefaultRouter()
router.register(r"", NotebookViewSet, basename="notebook")
urlpatterns = [path("", include(router.urls))]

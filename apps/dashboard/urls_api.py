from django.urls import path
from .views_api import DashboardStatsAPIView

urlpatterns = [
    path("stats/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
]

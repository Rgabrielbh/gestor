from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views_auth import LoginAPIView, LogoutAPIView, RegisterAPIView, MeAPIView, ChangePasswordAPIView

urlpatterns = [
    path("token/", LoginAPIView.as_view(), name="api-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="api-token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="api-token-verify"),
    path("logout/", LogoutAPIView.as_view(), name="api-logout"),
    path("register/", RegisterAPIView.as_view(), name="api-register"),
    path("me/", MeAPIView.as_view(), name="api-me"),
    path("me/change-password/", ChangePasswordAPIView.as_view(), name="api-change-password"),
]

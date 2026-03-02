from django.urls import path
from .views import (
    UsuarioListView, UsuarioCreateView, UsuarioUpdateView,
    UsuarioDeleteView, UsuarioResetPasswordView,
)
urlpatterns = [
    path('',                    UsuarioListView.as_view(),          name='usuarios-list'),
    path('novo/',               UsuarioCreateView.as_view(),        name='usuarios-create'),
    path('<int:pk>/editar/',    UsuarioUpdateView.as_view(),        name='usuarios-update'),
    path('<int:pk>/excluir/',   UsuarioDeleteView.as_view(),        name='usuarios-delete'),
    path('<int:pk>/senha/',     UsuarioResetPasswordView.as_view(), name='usuarios-reset-password'),
]

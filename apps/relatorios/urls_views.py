from django.urls import path
from .views_frontend import RelatoriosIndexView
urlpatterns = [
    path("", RelatoriosIndexView.as_view(), name="relatorios-index"),
]

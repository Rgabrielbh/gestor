from django.urls import path
from .views import TimelineIndexView, TimelineColaboradorView, TimelineNotebookView

app_name = "timeline"

urlpatterns = [
    path("",              TimelineIndexView.as_view(),     name="index"),
    path("colaboradores/",TimelineColaboradorView.as_view(),name="colaborador"),
    path("notebooks/",    TimelineNotebookView.as_view(),  name="notebook"),
]

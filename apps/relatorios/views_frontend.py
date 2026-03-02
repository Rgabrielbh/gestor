from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from apps.colaboradores.views_frontend import GestorRequired


class RelatoriosIndexView(LoginRequiredMixin, GestorRequired, TemplateView):
    template_name = "relatorios/index.html"

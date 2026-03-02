from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from apps.colaboradores.views_frontend import GestorRequired

from .models import Contrato
from .forms import ContratoForm
from django.utils import timezone

class ContratoListView(LoginRequiredMixin, ListView):
    model = Contrato; template_name = "contratos/list.html"; context_object_name = "contratos"; paginate_by = 20
    def get_queryset(self):
        qs = Contrato.objects.select_related("cliente").order_by("-dt_inicio")
        q = self.request.GET.get("q")
        if q: qs = qs.filter(codigo__icontains=q) | qs.filter(cliente__nome__icontains=q)
        ativo = self.request.GET.get("ativo")
        if ativo == "1": qs = qs.filter(dt_fim__gte=timezone.now().date())
        elif ativo == "0": qs = qs.filter(dt_fim__lt=timezone.now().date())
        return qs

class ContratoDetailView(LoginRequiredMixin, DetailView):
    model = Contrato; template_name = "contratos/detail.html"; context_object_name = "contrato"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projetos"] = self.object.projetos.filter(ativo=True)
        return ctx

class ContratoCreateView(LoginRequiredMixin, GestorRequired, CreateView):
    model = Contrato; form_class = ContratoForm; template_name = "contratos/form.html"
    success_url = reverse_lazy("contratos-list"); extra_context = {"titulo": _("Novo Contrato"), "action": _("Cadastrar")}
    def form_valid(self, form):
        messages.success(self.request, _("Contrato cadastrado.")); return super().form_valid(form)

class ContratoUpdateView(LoginRequiredMixin, GestorRequired, UpdateView):
    model = Contrato; form_class = ContratoForm; template_name = "contratos/form.html"
    extra_context = {"titulo": _("Editar Contrato"), "action": _("Salvar")}
    def get_success_url(self): return reverse_lazy("contratos-detail", kwargs={"pk": self.object.pk})
    def form_valid(self, form):
        messages.success(self.request, _("Contrato atualizado.")); return super().form_valid(form)

class ContratoDeleteView(LoginRequiredMixin, GestorRequired, DeleteView):
    model = Contrato; template_name = "contratos/confirm_delete.html"; success_url = reverse_lazy("contratos-list"); context_object_name = "contrato"
    def form_valid(self, form):
        messages.success(self.request, _("Contrato removido.")); return super().form_valid(form)

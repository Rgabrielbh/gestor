from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from apps.colaboradores.views_frontend import GestorRequired

from .models import Cliente
from .forms import ClienteForm

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente; template_name = "clientes/list.html"; context_object_name = "clientes"; paginate_by = 20
    def get_queryset(self):
        qs = Cliente.objects.order_by("nome")
        q = self.request.GET.get("q")
        if q: qs = qs.filter(nome__icontains=q) | qs.filter(cnpj__icontains=q)
        return qs

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente; template_name = "clientes/detail.html"; context_object_name = "cliente"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["projetos"] = self.object.projetos.filter(ativo=True).select_related("gestor")
        ctx["contratos"] = self.object.contratos.order_by("-dt_inicio")
        return ctx

class ClienteCreateView(LoginRequiredMixin, GestorRequired, CreateView):
    model = Cliente; form_class = ClienteForm; template_name = "clientes/form.html"
    success_url = reverse_lazy("clientes-list"); extra_context = {"titulo": _("Novo Cliente"), "action": _("Cadastrar")}
    def form_valid(self, form):
        messages.success(self.request, _("Cliente cadastrado.")); return super().form_valid(form)

class ClienteUpdateView(LoginRequiredMixin, GestorRequired, UpdateView):
    model = Cliente; form_class = ClienteForm; template_name = "clientes/form.html"
    extra_context = {"titulo": _("Editar Cliente"), "action": _("Salvar")}
    def get_success_url(self): return reverse_lazy("clientes-detail", kwargs={"pk": self.object.pk})
    def form_valid(self, form):
        messages.success(self.request, _("Cliente atualizado.")); return super().form_valid(form)

class ClienteDeleteView(LoginRequiredMixin, GestorRequired, DeleteView):
    model = Cliente; template_name = "clientes/confirm_delete.html"; success_url = reverse_lazy("clientes-list"); context_object_name = "cliente"
    def form_valid(self, form):
        messages.success(self.request, _("Cliente removido.")); return super().form_valid(form)

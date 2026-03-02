from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from apps.colaboradores.views_frontend import GestorRequired

from .models import Projeto, ColaboradorProjeto
from .forms import ProjetoForm, ColaboradorProjetoForm

class ProjetoListView(LoginRequiredMixin, ListView):
    model = Projeto; template_name = "projetos/list.html"; context_object_name = "projetos"; paginate_by = 20
    def get_queryset(self):
        qs = Projeto.objects.select_related("id_cliente","gestor").filter(ativo=True)
        q = self.request.GET.get("q")
        if q: qs = qs.filter(nome_proj_ntt__icontains=q) | qs.filter(ov__icontains=q)
        cliente = self.request.GET.get("cliente")
        if cliente: qs = qs.filter(id_cliente=cliente)
        return qs.order_by("nome_proj_ntt")

class ProjetoDetailView(LoginRequiredMixin, DetailView):
    model = Projeto; template_name = "projetos/detail.html"; context_object_name = "projeto"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["alocacoes"] = self.object.alocacoes.filter(dt_fim__isnull=True).select_related("id_colaborador")
        ctx["gestores_projeto"] = self.object.gestores_projeto.select_related("id_gp")
        return ctx

class ProjetoCreateView(LoginRequiredMixin, GestorRequired, CreateView):
    model = Projeto; form_class = ProjetoForm; template_name = "projetos/form.html"
    success_url = reverse_lazy("projetos-list"); extra_context = {"titulo": _("Novo Projeto"), "action": _("Cadastrar")}
    def form_valid(self, form):
        messages.success(self.request, _("Projeto criado.")); return super().form_valid(form)

class ProjetoUpdateView(LoginRequiredMixin, GestorRequired, UpdateView):
    model = Projeto; form_class = ProjetoForm; template_name = "projetos/form.html"
    extra_context = {"titulo": _("Editar Projeto"), "action": _("Salvar")}
    def get_success_url(self): return reverse_lazy("projetos-detail", kwargs={"pk": self.object.pk})
    def form_valid(self, form):
        messages.success(self.request, _("Projeto atualizado.")); return super().form_valid(form)

class ProjetoDeleteView(LoginRequiredMixin, GestorRequired, DeleteView):
    model = Projeto; template_name = "projetos/confirm_delete.html"; success_url = reverse_lazy("projetos-list"); context_object_name = "projeto"
    def form_valid(self, form):
        messages.success(self.request, _("Projeto removido.")); return super().form_valid(form)

class AlocacaoCreateView(LoginRequiredMixin, GestorRequired, CreateView):
    model = ColaboradorProjeto; form_class = ColaboradorProjetoForm; template_name = "projetos/alocacao_form.html"
    success_url = reverse_lazy("projetos-list"); extra_context = {"titulo": _("Nova Alocação"), "action": _("Alocar")}
    def form_valid(self, form):
        messages.success(self.request, _("Colaborador alocado com sucesso.")); return super().form_valid(form)

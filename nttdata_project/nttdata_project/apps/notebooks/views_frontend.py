from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from apps.colaboradores.views_frontend import GestorRequired

from .models import Notebook
from .forms import NotebookForm

class NotebookListView(LoginRequiredMixin, ListView):
    model = Notebook; template_name = "notebooks/list.html"; context_object_name = "notebooks"; paginate_by = 20
    def get_queryset(self):
        qs = Notebook.objects.select_related("responsavel").all()
        q = self.request.GET.get("q")
        if q: qs = qs.filter(numero_serie__icontains=q) | qs.filter(responsavel__nome__icontains=q) | qs.filter(modelo__icontains=q)
        return qs.order_by("numero_serie")

class NotebookDetailView(LoginRequiredMixin, DetailView):
    model = Notebook; template_name = "notebooks/detail.html"; context_object_name = "notebook"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["historico"] = self.object.historico.select_related(
            "responsavel", "cliente"
        ).order_by("dt_inicio")
        return ctx

class NotebookCreateView(LoginRequiredMixin, GestorRequired, CreateView):
    model = Notebook; form_class = NotebookForm; template_name = "notebooks/form.html"
    success_url = reverse_lazy("notebooks-list"); extra_context = {"titulo": _("Novo Notebook"), "action": _("Cadastrar")}
    def form_valid(self, form):
        messages.success(self.request, _("Notebook cadastrado.")); return super().form_valid(form)

class NotebookUpdateView(LoginRequiredMixin, GestorRequired, UpdateView):
    model = Notebook; form_class = NotebookForm; template_name = "notebooks/form.html"
    extra_context = {"titulo": _("Editar Notebook"), "action": _("Salvar")}
    def get_success_url(self): return reverse_lazy("notebooks-detail", kwargs={"pk": self.object.pk})
    def form_valid(self, form):
        messages.success(self.request, _("Notebook atualizado.")); return super().form_valid(form)

class NotebookDeleteView(LoginRequiredMixin, GestorRequired, DeleteView):
    model = Notebook; template_name = "notebooks/confirm_delete.html"; success_url = reverse_lazy("notebooks-list"); context_object_name = "notebook"
    def form_valid(self, form):
        messages.success(self.request, _("Notebook removido.")); return super().form_valid(form)


def notebook_historico_json(request, pk):
    from apps.notebooks.models import Notebook
    from django.shortcuts import get_object_or_404
    nb = get_object_or_404(Notebook, pk=pk)
    historico = []
    for h in nb.historico.select_related("responsavel", "cliente").order_by("dt_inicio"):
        historico.append({
            "responsavel": h.responsavel.nome if h.responsavel else None,
            "cargo":       h.responsavel.cargo if h.responsavel else None,
            "cliente":     h.cliente.nome if h.cliente else None,
            "localizacao": h.localizacao or None,
            "dt_inicio":   h.dt_inicio.strftime("%d/%m/%Y") if h.dt_inicio else None,
            "dt_fim":      h.dt_fim.strftime("%d/%m/%Y") if h.dt_fim else None,
            "duracao":     h.duracao,
            "observacao":  h.observacao or None,
        })
    return JsonResponse({
        "historico":         historico,
        "patrimonio_ntt":    nb.patrimonio_ntt or None,
        "patrimonio_cliente":nb.patrimonio_cliente or None,
        "localizacao":       nb.localizacao or None,
    })

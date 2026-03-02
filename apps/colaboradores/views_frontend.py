from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import LoginForm, RegisterForm, ColaboradorUpdateForm, ProfileUpdateForm
from .models import Colaborador, RoleChoices


class GestorRequired(UserPassesTestMixin):
    def test_func(self): return self.request.user.role in (RoleChoices.DIRETOR, RoleChoices.GESTOR)
    def handle_no_permission(self):
        messages.error(self.request, _("Acesso negado. Apenas Gestores e Diretores."))
        return redirect("dashboard:index")


class LoginView(View):
    template_name = "registration/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:index")
        return render(request, self.template_name, {"form": LoginForm(request)})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)
            messages.success(request, _("Bem-vindo(a), %(nome)s!") % {"nome": user.nome_display})
            return redirect(request.GET.get("next", "dashboard:index"))
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, _("Sessão encerrada."))
        return redirect("login")
    def get(self, request):
        logout(request)
        return redirect("login")


class RegisterView(LoginRequiredMixin, GestorRequired, View):
    template_name = "registration/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            c = form.save()
            messages.success(request, _("Colaborador %(nome)s criado com sucesso.") % {"nome": c.nome})
            return redirect("colaboradores-detail", pk=c.pk)
        return render(request, self.template_name, {"form": form})


class ProfileView(LoginRequiredMixin, View):
    template_name = "colaboradores/profile.html"

    def get(self, request):
        form = ProfileUpdateForm(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Perfil atualizado."))
            return redirect("profile")
        return render(request, self.template_name, {"form": form})


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = "registration/change_password.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PasswordChangeForm(request.user)})

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            update_session_auth_hash(request, form.save())
            messages.success(request, _("Senha alterada com sucesso."))
            return redirect("profile")
        return render(request, self.template_name, {"form": form})


class ColaboradorListView(LoginRequiredMixin, ListView):
    model = Colaborador
    template_name = "colaboradores/list.html"
    context_object_name = "colaboradores"
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        qs = Colaborador.objects.select_related("gestor_direto").order_by("nome")
        if user.role == RoleChoices.OPERADOR:
            qs = qs.filter(pk=user.pk)
        elif user.role == RoleChoices.GERENTE_PROJETO:
            qs = qs.filter(gestor_direto=user) | qs.filter(pk=user.pk)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q) | qs.filter(email__icontains=q) | qs.filter(matricula__icontains=q)
        role_f = self.request.GET.get("role")
        if role_f:
            qs = qs.filter(role=role_f)
        status_f = self.request.GET.get("status")
        if status_f:
            qs = qs.filter(status=status_f)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["roles"] = RoleChoices.choices
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ColaboradorDetailView(LoginRequiredMixin, DetailView):
    model = Colaborador
    template_name = "colaboradores/detail.html"
    context_object_name = "colaborador"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["alocacoes_ativas"] = self.object.alocacoes.filter(dt_fim__isnull=True).select_related("id_proj","id_cliente")
        ctx["notebooks"] = self.object.notebooks.filter(ativo=True)
        return ctx


class ColaboradorCreateView(LoginRequiredMixin, GestorRequired, CreateView):
    model = Colaborador
    form_class = RegisterForm
    template_name = "colaboradores/form.html"
    success_url = reverse_lazy("colaboradores-list")
    extra_context = {"titulo": _("Novo Colaborador"), "action": _("Cadastrar")}

    def form_valid(self, form):
        messages.success(self.request, _("Colaborador criado com sucesso."))
        return super().form_valid(form)


class ColaboradorUpdateView(LoginRequiredMixin, GestorRequired, UpdateView):
    model = Colaborador
    form_class = ColaboradorUpdateForm
    template_name = "colaboradores/form.html"
    extra_context = {"titulo": _("Editar Colaborador"), "action": _("Salvar")}

    def get_success_url(self):
        return reverse_lazy("colaboradores-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _("Colaborador atualizado."))
        return super().form_valid(form)


class ColaboradorDeleteView(LoginRequiredMixin, GestorRequired, DeleteView):
    model = Colaborador
    template_name = "colaboradores/confirm_delete.html"
    success_url = reverse_lazy("colaboradores-list")
    context_object_name = "colaborador"

    def form_valid(self, form):
        messages.success(self.request, _("Colaborador removido."))
        return super().form_valid(form)

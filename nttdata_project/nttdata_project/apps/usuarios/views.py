from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from apps.colaboradores.models import Colaborador, RoleChoices
from apps.colaboradores.forms import RegisterForm, ColaboradorUpdateForm


def diretor_gestor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in (RoleChoices.DIRETOR, RoleChoices.GESTOR):
            messages.error(request, _("Acesso restrito a gestores."))
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@method_decorator([login_required, diretor_gestor_required], name='dispatch')
class UsuarioListView(View):
    def get(self, request):
        q    = request.GET.get('q', '')
        role = request.GET.get('role', '')
        status = request.GET.get('status', '')
        qs = Colaborador.objects.all().order_by('nome')
        if q:
            qs = qs.filter(Q(nome__icontains=q) | Q(email__icontains=q) | Q(username__icontains=q) | Q(matricula__icontains=q))
        if role:
            qs = qs.filter(role=role)
        if status:
            qs = qs.filter(status=status)
        return render(request, 'usuarios/list.html', {
            'usuarios': qs,
            'q': q,
            'role': role,
            'status': status,
            'roles': RoleChoices.choices,
            'total': qs.count(),
        })


@method_decorator([login_required, diretor_gestor_required], name='dispatch')
class UsuarioCreateView(View):
    def get(self, request):
        return render(request, 'usuarios/form.html', {
            'form': RegisterForm(),
            'titulo': _('Novo Usuário'),
            'action': _('Cadastrar'),
        })

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, _(f"Usuário {user.nome} criado com sucesso."))
            return redirect('usuarios-list')
        return render(request, 'usuarios/form.html', {
            'form': form,
            'titulo': _('Novo Usuário'),
            'action': _('Cadastrar'),
        })


@method_decorator([login_required, diretor_gestor_required], name='dispatch')
class UsuarioUpdateView(View):
    def get(self, request, pk):
        usuario = get_object_or_404(Colaborador, pk=pk)
        form = UsuarioAdminForm(instance=usuario)
        return render(request, 'usuarios/form.html', {
            'form': form,
            'usuario': usuario,
            'titulo': _('Editar Usuário'),
            'action': _('Salvar'),
        })

    def post(self, request, pk):
        usuario = get_object_or_404(Colaborador, pk=pk)
        form = UsuarioAdminForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, _(f"Usuário {usuario.nome} atualizado."))
            return redirect('usuarios-list')
        return render(request, 'usuarios/form.html', {
            'form': form,
            'usuario': usuario,
            'titulo': _('Editar Usuário'),
            'action': _('Salvar'),
        })


@method_decorator([login_required, diretor_gestor_required], name='dispatch')
class UsuarioDeleteView(View):
    def get(self, request, pk):
        usuario = get_object_or_404(Colaborador, pk=pk)
        return render(request, 'usuarios/confirm_delete.html', {'usuario': usuario})

    def post(self, request, pk):
        usuario = get_object_or_404(Colaborador, pk=pk)
        if usuario.pk == request.user.pk:
            messages.error(request, _("Você não pode excluir sua própria conta."))
            return redirect('usuarios-list')
        nome = usuario.nome
        usuario.delete()
        messages.success(request, _(f"Usuário {nome} excluído."))
        return redirect('usuarios-list')


@method_decorator([login_required, diretor_gestor_required], name='dispatch')
class UsuarioResetPasswordView(View):
    def get(self, request, pk):
        usuario = get_object_or_404(Colaborador, pk=pk)
        return render(request, 'usuarios/reset_password.html', {'usuario': usuario})

    def post(self, request, pk):
        usuario = get_object_or_404(Colaborador, pk=pk)
        nova_senha = request.POST.get('password1')
        confirma   = request.POST.get('password2')
        if not nova_senha or nova_senha != confirma:
            messages.error(request, _("As senhas não coincidem."))
            return render(request, 'usuarios/reset_password.html', {'usuario': usuario})
        if len(nova_senha) < 8:
            messages.error(request, _("A senha deve ter pelo menos 8 caracteres."))
            return render(request, 'usuarios/reset_password.html', {'usuario': usuario})
        usuario.set_password(nova_senha)
        usuario.save()
        if usuario.pk == request.user.pk:
            update_session_auth_hash(request, usuario)
        messages.success(request, _(f"Senha de {usuario.nome} redefinida."))
        return redirect('usuarios-list')


# Form de edição admin (sem senha obrigatória)
from django import forms as dj_forms

class UsuarioAdminForm(dj_forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ['nome', 'email', 'username', 'role', 'status',
                  'matricula', 'cargo', 'funcao', 'telefone',
                  'cidade', 'estado', 'dt_admissao', 'gestor_direto', 'is_active']
        widgets = {
            'nome':        dj_forms.TextInput(attrs={'class': 'form-control'}),
            'email':       dj_forms.EmailInput(attrs={'class': 'form-control'}),
            'username':    dj_forms.TextInput(attrs={'class': 'form-control'}),
            'role':        dj_forms.Select(attrs={'class': 'form-select'}),
            'status':      dj_forms.Select(attrs={'class': 'form-select'}),
            'matricula':   dj_forms.TextInput(attrs={'class': 'form-control'}),
            'cargo':       dj_forms.TextInput(attrs={'class': 'form-control'}),
            'funcao':      dj_forms.TextInput(attrs={'class': 'form-control'}),
            'telefone':    dj_forms.TextInput(attrs={'class': 'form-control'}),
            'cidade':      dj_forms.TextInput(attrs={'class': 'form-control'}),
            'estado':      dj_forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'dt_admissao': dj_forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gestor_direto': dj_forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gestor_direto'].queryset = Colaborador.objects.filter(
            role__in=['diretor', 'gestor', 'gerente_projeto']
        )
        self.fields['gestor_direto'].required = False
        for f in ['matricula','cargo','funcao','telefone','cidade','estado','dt_admissao']:
            self.fields[f].required = False

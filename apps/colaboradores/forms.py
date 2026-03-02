from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import Colaborador, RoleChoices, StatusColaborador


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Usuário ou e-mail"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": _("Usuário ou e-mail"), "autofocus": True}),
    )
    password = forms.CharField(
        label=_("Senha"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": _("Senha")}),
    )
    remember_me = forms.BooleanField(label=_("Manter conectado"), required=False,
                                     widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()
        if "@" in username:
            try:
                user = Colaborador.objects.get(email__iexact=username)
                return user.username
            except Colaborador.DoesNotExist:
                pass
        return username


class RegisterForm(UserCreationForm):
    nome = forms.CharField(label=_("Nome completo"), max_length=255,
                           widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label=_("E-mail"), widget=forms.EmailInput(attrs={"class": "form-control"}))
    role = forms.ChoiceField(label=_("Perfil de acesso"), choices=RoleChoices.choices,
                             initial=RoleChoices.OPERADOR, widget=forms.Select(attrs={"class": "form-select"}))
    matricula = forms.CharField(label=_("Matrícula"), required=False,
                                widget=forms.TextInput(attrs={"class": "form-control"}))
    cargo = forms.CharField(label=_("Cargo"), required=False,
                            widget=forms.TextInput(attrs={"class": "form-control"}))
    funcao = forms.CharField(label=_("Função"), required=False,
                             widget=forms.TextInput(attrs={"class": "form-control"}))
    cidade = forms.CharField(label=_("Cidade"), required=False,
                             widget=forms.TextInput(attrs={"class": "form-control"}))
    estado = forms.CharField(label=_("Estado"), required=False, max_length=2,
                             widget=forms.TextInput(attrs={"class": "form-control"}))
    telefone = forms.CharField(label=_("Telefone"), required=False,
                               widget=forms.TextInput(attrs={"class": "form-control"}))
    dt_admissao = forms.DateField(label=_("Data de admissão"), required=False,
                                  widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}))
    gestor_direto = forms.ModelChoiceField(
        label=_("Gestor direto"), required=False,
        queryset=Colaborador.objects.filter(role__in=["gestor", "gerente_projeto", "diretor"]),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Colaborador
        fields = ["username","nome","email","role","matricula","cargo","funcao","telefone",
                  "cidade","estado","dt_admissao","gestor_direto","password1","password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Colaborador.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("Este e-mail já está cadastrado."))
        return email.lower()


class ColaboradorUpdateForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["nome","email","telefone","cidade","estado","local_escritorio",
                  "cargo","funcao","matricula","pos","req","dt_admissao","dt_demissao",
                  "status","role","gestor_direto","cod_gestor","nome_gestor","salario","avatar"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "telefone": forms.TextInput(attrs={"class": "form-control"}),
            "cidade": forms.TextInput(attrs={"class": "form-control"}),
            "estado": forms.TextInput(attrs={"class": "form-control"}),
            "local_escritorio": forms.TextInput(attrs={"class": "form-control"}),
            "cargo": forms.TextInput(attrs={"class": "form-control"}),
            "funcao": forms.TextInput(attrs={"class": "form-control"}),
            "matricula": forms.TextInput(attrs={"class": "form-control"}),
            "pos": forms.TextInput(attrs={"class": "form-control"}),
            "req": forms.TextInput(attrs={"class": "form-control"}),
            "dt_admissao": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "dt_demissao": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "gestor_direto": forms.Select(attrs={"class": "form-select"}),
            "cod_gestor": forms.TextInput(attrs={"class": "form-control"}),
            "nome_gestor": forms.TextInput(attrs={"class": "form-control"}),
            "salario": forms.NumberInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Colaborador
        fields = ["nome","email","telefone","cidade","estado","local_escritorio","cargo","funcao","avatar"]
        widgets = {
            f: forms.TextInput(attrs={"class": "form-control"})
            for f in ["nome","telefone","cidade","estado","local_escritorio","cargo","funcao"]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["avatar"].widget.attrs.update({"class": "form-control"})

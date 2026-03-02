from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class RoleChoices(models.TextChoices):
    DIRETOR = "diretor", _("Diretor")
    GESTOR = "gestor", _("Gestor")
    GERENTE_PROJETO = "gerente_projeto", _("Gerente de Projeto")
    OPERADOR = "operador", _("Operador")


class StatusColaborador(models.TextChoices):
    ATIVO = "ativo", _("Ativo")
    INATIVO = "inativo", _("Inativo")
    AFASTADO = "afastado", _("Afastado")


telefone_validator = RegexValidator(r"^\+?[\d\s\(\)\-]{8,20}$", _("Telefone inválido."))


class Colaborador(AbstractUser):
    """
    Usuário do sistema. Cada colaborador tem credenciais de acesso.
    A role determina o nível hierárquico e as permissões.
    """
    email = models.EmailField(_("e-mail"), unique=True)
    nome = models.CharField(_("nome completo"), max_length=255)
    matricula = models.CharField(_("matrícula"), max_length=50, unique=True, null=True, blank=True)
    pos = models.CharField(_("posição"), max_length=50, blank=True)
    req = models.CharField(_("requisição"), max_length=50, blank=True)
    cargo = models.CharField(_("cargo"), max_length=100, blank=True)
    funcao = models.CharField(_("função"), max_length=100, blank=True)
    telefone = models.CharField(_("telefone"), max_length=20, blank=True, validators=[telefone_validator])
    cidade = models.CharField(_("cidade"), max_length=100, blank=True)
    estado = models.CharField(_("estado"), max_length=50, blank=True)
    local_escritorio = models.CharField(_("local do escritório"), max_length=100, blank=True)
    dt_admissao = models.DateField(_("data de admissão"), null=True, blank=True)
    dt_demissao = models.DateField(_("data de demissão"), null=True, blank=True)
    salario = models.DecimalField(_("salário"), max_digits=12, decimal_places=2, null=True, blank=True)
    cod_gestor_sup = models.CharField(_("cód. gestor superior"), max_length=50, blank=True)
    cod_gestor = models.CharField(_("cód. gestor"), max_length=50, blank=True)
    nome_gestor = models.CharField(_("nome do gestor"), max_length=255, blank=True)
    gestor_direto = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="subordinados", verbose_name=_("gestor direto"),
    )
    status = models.CharField(_("status"), max_length=20, choices=StatusColaborador.choices, default=StatusColaborador.ATIVO)
    role = models.CharField(_("perfil"), max_length=20, choices=RoleChoices.choices, default=RoleChoices.OPERADOR)
    avatar = models.ImageField(_("foto"), upload_to="avatars/", null=True, blank=True)

    REQUIRED_FIELDS = ["nome", "email"]

    class Meta:
        verbose_name = _("colaborador")
        verbose_name_plural = _("colaboradores")
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["status"]),
            models.Index(fields=["matricula"]),
        ]

    def __str__(self):
        return f"{self.nome} ({self.get_role_display()})"

    @property
    def is_diretor(self): return self.role == RoleChoices.DIRETOR
    @property
    def is_gestor_ou_superior(self): return self.role in (RoleChoices.DIRETOR, RoleChoices.GESTOR)
    @property
    def is_gerente_ou_superior(self): return self.role in (RoleChoices.DIRETOR, RoleChoices.GESTOR, RoleChoices.GERENTE_PROJETO)
    @property
    def nome_display(self): return self.nome or self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        if self.nome:
            partes = self.nome.strip().split(" ", 1)
            self.first_name = partes[0]
            self.last_name = partes[1] if len(partes) > 1 else ""
        if self.role in (RoleChoices.DIRETOR, RoleChoices.GESTOR):
            self.is_staff = True
        super().save(*args, **kwargs)

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


cnpj_validator = RegexValidator(
    r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$",
    _("CNPJ inválido. Use o formato XX.XXX.XXX/XXXX-XX.")
)


class Cliente(models.Model):
    cnpj = models.CharField(_("CNPJ"), max_length=18, unique=True, validators=[cnpj_validator])
    nome = models.CharField(_("nome"), max_length=255)
    resp_nttdata = models.CharField(_("responsável NTT Data"), max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("cliente")
        verbose_name_plural = _("clientes")
        ordering = ["nome"]
        indexes = [models.Index(fields=["cnpj"])]

    def __str__(self):
        return self.nome

    @property
    def contratos_ativos(self):
        from django.utils import timezone
        return self.contratos.filter(dt_fim__gte=timezone.now().date())

    @property
    def total_colaboradores(self):
        from apps.projetos.models import ColaboradorProjeto
        return ColaboradorProjeto.objects.filter(
            id_cliente=self, dt_fim__isnull=True
        ).values("id_colaborador").distinct().count()

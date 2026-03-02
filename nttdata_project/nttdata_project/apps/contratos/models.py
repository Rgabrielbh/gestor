from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.clientes.models import Cliente


class Contrato(models.Model):
    codigo = models.CharField(_("código"), max_length=50, unique=True)
    descricao = models.TextField(_("descrição"), blank=True)
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE,
        related_name="contratos", verbose_name=_("cliente"), null=True, blank=True
    )
    fte = models.FloatField(_("FTE (Full-Time Equivalent)"), default=0)
    dt_inicio = models.DateField(_("data de início"))
    dt_fim = models.DateField(_("data de término"))
    renova = models.BooleanField(_("renovável"), default=False)
    ov_anterior = models.CharField(_("OV anterior"), max_length=50, blank=True)
    resp_cliente = models.CharField(_("responsável do cliente"), max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("contrato")
        verbose_name_plural = _("contratos")
        ordering = ["-dt_inicio"]

    def __str__(self):
        return f"{self.codigo} — {self.cliente}"

    @property
    def ativo(self):
        from django.utils import timezone
        return self.dt_fim >= timezone.now().date()

    @property
    def dias_para_vencimento(self):
        from django.utils import timezone
        return (self.dt_fim - timezone.now().date()).days

from django.db import models
from django.utils.translation import gettext_lazy as _


class Notebook(models.Model):
    numero_serie = models.CharField(_("número de série"), max_length=50, unique=True)
    eh_ntt = models.BooleanField(_("é da NTT Data"), default=False)
    patrimonio_ntt = models.CharField(_("patrimônio NTT"), max_length=50, blank=True, null=True)
    eh_cliente = models.BooleanField(_("é do cliente"), default=False)
    patrimonio_cliente = models.CharField(_("patrimônio cliente"), max_length=50, blank=True, null=True)
    localizacao = models.CharField(_("localização"), max_length=255, blank=True)
    responsavel = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="notebooks",
        verbose_name=_("responsável")
    )
    modelo = models.CharField(_("modelo"), max_length=100, blank=True)
    marca = models.CharField(_("marca"), max_length=100, blank=True)
    ativo = models.BooleanField(_("ativo"), default=True)
    observacoes = models.TextField(_("observações"), blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("notebook")
        verbose_name_plural = _("notebooks")
        ordering = ["numero_serie"]

    def __str__(self):
        return f"{self.numero_serie} — {self.responsavel or 'Sem responsável'}"

    @property
    def origem(self):
        if self.eh_ntt:
            return "NTT Data"
        if self.eh_cliente:
            return "Cliente"
        return "Outro"


class NotebookHistorico(models.Model):
    """Rastreabilidade de posse e localização de notebooks."""
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE,
        related_name="historico", verbose_name=_("notebook")
    )
    responsavel = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="historico_notebooks",
        verbose_name=_("responsável")
    )
    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="historico_notebooks",
        verbose_name=_("cliente")
    )
    localizacao = models.CharField(_("localização"), max_length=255, blank=True)
    dt_inicio = models.DateField(_("data de início"))
    dt_fim = models.DateField(_("data de término"), null=True, blank=True)
    observacao = models.TextField(_("observação"), blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("histórico de notebook")
        verbose_name_plural = _("históricos de notebooks")
        ordering = ["-dt_inicio"]
        indexes = [
            models.Index(fields=["notebook"]),
            models.Index(fields=["responsavel"]),
        ]

    def __str__(self):
        resp = self.responsavel.nome if self.responsavel else "Sem responsável"
        return f"{self.notebook.numero_serie} → {resp} ({self.dt_inicio})"

    @property
    def ativo(self):
        return self.dt_fim is None

    @property
    def duracao(self):
        from django.utils import timezone
        fim = self.dt_fim or timezone.now().date()
        delta = fim - self.dt_inicio
        anos = delta.days // 365
        meses = (delta.days % 365) // 30
        dias = (delta.days % 365) % 30
        partes = []
        if anos: partes.append(f"{anos} ano{'s' if anos > 1 else ''}")
        if meses: partes.append(f"{meses} {'meses' if meses > 1 else 'mês'}")
        if dias or not partes: partes.append(f"{dias} dia{'s' if dias != 1 else ''}")
        return ", ".join(partes)

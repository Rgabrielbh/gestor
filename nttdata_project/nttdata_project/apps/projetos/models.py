from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.clientes.models import Cliente


class Projeto(models.Model):
    nome_proj_ntt = models.CharField(_("nome do projeto (NTT)"), max_length=255)
    descricao = models.TextField(_("descrição"), blank=True)
    id_cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE,
        related_name="projetos", verbose_name=_("cliente")
    )
    contrato = models.ForeignKey(
        "contratos.Contrato", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="projetos", verbose_name=_("contrato")
    )
    qte_pessoas = models.IntegerField(_("quantidade prevista de pessoas"), default=0)
    qte_pessoas_atual = models.IntegerField(_("quantidade atual de pessoas"), default=0)
    contrato_pend = models.BooleanField(_("contrato pendente"), default=False)
    ov = models.CharField(_("OV"), max_length=50, blank=True)
    gestor = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="projetos_gerenciados",
        verbose_name=_("gestor do projeto")
    )
    ativo = models.BooleanField(_("ativo"), default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("projeto")
        verbose_name_plural = _("projetos")
        ordering = ["nome_proj_ntt"]

    def __str__(self):
        return f"{self.nome_proj_ntt} — {self.id_cliente}"

    @property
    def percentual_alocacao(self):
        if self.qte_pessoas == 0:
            return 0
        return round((self.qte_pessoas_atual / self.qte_pessoas) * 100, 1)


class GestorProjeto(models.Model):
    """Relacionamento entre Gestor de Projeto e Projeto (permite múltiplos GPs por projeto)."""
    id_projeto = models.ForeignKey(
        Projeto, on_delete=models.CASCADE,
        related_name="gestores_projeto", verbose_name=_("projeto")
    )
    nome_proj = models.CharField(_("nome do projeto"), max_length=255)
    id_cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, verbose_name=_("cliente")
    )
    id_gp = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.CASCADE,
        related_name="gestoes", verbose_name=_("gerente de projeto")
    )
    id_colaborador = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.CASCADE,
        related_name="alocacoes_gp", verbose_name=_("colaborador"),
        null=True, blank=True,
        help_text=_("Colaborador específico sob a gestão deste GP neste projeto.")
    )
    nome_colaborador = models.CharField(_("nome do colaborador"), max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("gestor de projeto")
        verbose_name_plural = _("gestores de projeto")

    def __str__(self):
        return f"GP {self.id_gp.nome} — {self.nome_proj}"

    @property
    def tot_colaboradores(self):
        return ColaboradorProjeto.objects.filter(
            id_proj=self.id_projeto, dt_fim__isnull=True
        ).count()


class ColaboradorProjeto(models.Model):
    """Alocação de um colaborador em um projeto (M2M com atributos)."""
    id_proj = models.ForeignKey(
        Projeto, on_delete=models.CASCADE,
        related_name="alocacoes", verbose_name=_("projeto")
    )
    nome_proj = models.CharField(_("nome do projeto"), max_length=255)
    ov_projeto = models.CharField(_("OV do projeto"), max_length=50, blank=True)
    id_cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, verbose_name=_("cliente")
    )
    id_colaborador = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.CASCADE,
        related_name="alocacoes", verbose_name=_("colaborador")
    )
    nome_colaborador = models.CharField(_("nome do colaborador"), max_length=255, blank=True)
    centro_custo = models.CharField(_("centro de custo"), max_length=50, blank=True)
    custo_projeto = models.BooleanField(_("custo no projeto"), default=True)
    funcao = models.CharField(_("função"), max_length=100, blank=True)
    dt_inicio = models.DateField(_("data de início"))
    dt_fim = models.DateField(_("data de término"), null=True, blank=True)
    squad = models.CharField(_("squad"), max_length=100, blank=True)
    contato_projeto = models.CharField(_("contato do projeto"), max_length=255, blank=True)
    resp_cliente = models.CharField(_("responsável do cliente"), max_length=255, blank=True)
    p01 = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="alocacoes_p01",
        verbose_name=_("Project Owner 1")
    )
    p02 = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="alocacoes_p02",
        verbose_name=_("Project Owner 2")
    )
    gestor = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="alocacoes_como_gestor",
        verbose_name=_("gestor")
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("alocação de colaborador")
        verbose_name_plural = _("alocações de colaboradores")
        ordering = ["-dt_inicio"]
        indexes = [
            models.Index(fields=["dt_inicio", "dt_fim"]),
            models.Index(fields=["id_colaborador"]),
        ]

    def __str__(self):
        return f"{self.nome_colaborador} — {self.nome_proj}"

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

    def save(self, *args, **kwargs):
        if self.id_colaborador_id and not self.nome_colaborador:
            self.nome_colaborador = self.id_colaborador.nome
        if self.id_proj_id and not self.nome_proj:
            self.nome_proj = self.id_proj.nome_proj_ntt
        super().save(*args, **kwargs)


# ── Alocação parcial (divisão de horas por projeto) ──────────────────────────

class AlocacaoParcial(models.Model):
    """
    Permite que um colaborador seja alocado em múltiplos projetos
    com divisão de horas por dia.
    Total de horas_dia de todas as alocações ativas de um colaborador
    não deve exceder 8h.
    """
    JORNADA_MAX = 8

    id_colaborador = models.ForeignKey(
        "colaboradores.Colaborador", on_delete=models.CASCADE,
        related_name="alocacoes_parciais", verbose_name=_("colaborador")
    )
    id_alocacao = models.ForeignKey(
        ColaboradorProjeto, on_delete=models.CASCADE,
        related_name="alocacoes_parciais", verbose_name=_("alocação")
    )
    horas_dia = models.DecimalField(
        _("horas por dia"), max_digits=4, decimal_places=1,
        help_text=_("Horas diárias dedicadas a este projeto (máx. 8h total)")
    )
    dt_inicio = models.DateField(_("data de início"))
    dt_fim = models.DateField(_("data de término"), null=True, blank=True)
    observacao = models.TextField(_("observação"), blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("alocação parcial")
        verbose_name_plural = _("alocações parciais")
        ordering = ["-dt_inicio"]
        indexes = [
            models.Index(fields=["id_colaborador", "dt_fim"]),
        ]

    def __str__(self):
        return (f"{self.id_colaborador.nome} → "
                f"{self.id_alocacao.id_proj.nome_proj_ntt} "
                f"({self.horas_dia}h/dia)")

    @property
    def ativo(self):
        return self.dt_fim is None

    @property
    def percentual_dia(self):
        """Percentual do dia de trabalho (base 8h)."""
        return round(float(self.horas_dia) / self.JORNADA_MAX * 100, 1)

    @property
    def turno_descricao(self):
        """Descrição amigável do turno baseada nas horas."""
        h = float(self.horas_dia)
        if h <= 2:
            return "Suporte pontual"
        elif h <= 4:
            return "Meio período"
        elif h < 8:
            return "Dedicação parcial"
        return "Dedicação integral"

    @classmethod
    def horas_usadas(cls, colaborador, excluir_pk=None):
        """Soma de horas ativas do colaborador (para validação)."""
        qs = cls.objects.filter(
            id_colaborador=colaborador, dt_fim__isnull=True
        )
        if excluir_pk:
            qs = qs.exclude(pk=excluir_pk)
        from django.db.models import Sum
        result = qs.aggregate(total=Sum("horas_dia"))["total"]
        return float(result or 0)

    def clean(self):
        from django.core.exceptions import ValidationError
        usadas = self.horas_usadas(self.id_colaborador, excluir_pk=self.pk)
        if self.dt_fim is None:  # só valida alocações ativas
            if usadas + float(self.horas_dia) > self.JORNADA_MAX:
                disponivel = self.JORNADA_MAX - usadas
                raise ValidationError(
                    f"Jornada excedida. "
                    f"O colaborador tem {usadas}h alocadas. "
                    f"Disponível: {disponivel}h"
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

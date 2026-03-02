from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Count, Q, Avg


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        from apps.colaboradores.models import Colaborador, StatusColaborador
        from apps.clientes.models import Cliente
        from apps.contratos.models import Contrato
        from apps.projetos.models import Projeto, ColaboradorProjeto
        from apps.notebooks.models import Notebook
        from datetime import timedelta

        ctx = super().get_context_data(**kwargs)
        hoje = timezone.now().date()
        primeiro_dia_mes = hoje.replace(day=1)
        trinta_dias = hoje + timedelta(days=30)
        sessenta_dias = hoje + timedelta(days=60)

        # ── KPIs principais ────────────────────────────────────────────
        total_colaboradores = Colaborador.objects.filter(
            status=StatusColaborador.ATIVO, is_active=True
        ).count()

        total_projetos = Projeto.objects.filter(ativo=True).count()
        contratos_vigentes = Contrato.objects.filter(dt_fim__gte=hoje).count()
        alocacoes_ativas = ColaboradorProjeto.objects.filter(dt_fim__isnull=True).count()

        # Colaboradores sem alocação ativa
        colaboradores_alocados_ids = ColaboradorProjeto.objects.filter(
            dt_fim__isnull=True
        ).values_list('id_colaborador_id', flat=True)
        colaboradores_sem_alocacao = Colaborador.objects.filter(
            status=StatusColaborador.ATIVO, is_active=True
        ).exclude(id__in=colaboradores_alocados_ids).count()

        # ── Alertas críticos ───────────────────────────────────────────
        contratos_vencendo_30 = Contrato.objects.filter(
            dt_fim__gte=hoje, dt_fim__lte=trinta_dias
        ).select_related('cliente').order_by('dt_fim')

        contratos_vencendo_60 = Contrato.objects.filter(
            dt_fim__gt=trinta_dias, dt_fim__lte=sessenta_dias
        ).count()

        projetos_sem_contrato = Projeto.objects.filter(
            ativo=True, contrato_pend=True
        ).count()

        projetos_sub_alocados = Projeto.objects.filter(ativo=True).count()  # calculado no template via property

        # ── Projetos por status de alocação ────────────────────────────
        projetos_qs = Projeto.objects.filter(ativo=True).select_related('id_cliente', 'gestor')
        criticos, atencao, saudaveis = [], [], []
        for p in projetos_qs:
            perc = p.percentual_alocacao
            if perc < 50:
                criticos.append(p)
            elif perc < 80:
                atencao.append(p)
            else:
                saudaveis.append(p)

        # ── Headcount por cliente ──────────────────────────────────────
        headcount_por_cliente = list(
            ColaboradorProjeto.objects.filter(dt_fim__isnull=True)
            .values('id_cliente__nome')
            .annotate(total=Count('id'))
            .order_by('-total')[:6]
        )

        # ── Contratos vencendo (tabela) ────────────────────────────────
        contratos_proximos = Contrato.objects.filter(
            dt_fim__gte=hoje, dt_fim__lte=sessenta_dias
        ).select_related('cliente').order_by('dt_fim')[:6]

        # ── Projetos recentes / top ────────────────────────────────────
        projetos_recentes = Projeto.objects.filter(ativo=True).select_related(
            'id_cliente', 'gestor'
        ).order_by('-criado_em')[:6]

        # ── Admissões no mês ───────────────────────────────────────────
        colaboradores_recentes = Colaborador.objects.filter(
            dt_admissao__gte=primeiro_dia_mes
        ).order_by('-dt_admissao')[:5]

        # ── Distribuição de alocações por projeto (para gráfico) ───────
        alocacoes_por_projeto = list(
            ColaboradorProjeto.objects.filter(dt_fim__isnull=True)
            .values('id_proj__nome_proj_ntt')
            .annotate(total=Count('id'))
            .order_by('-total')[:7]
        )

        ctx.update({
            "hoje": hoje,
            # KPIs
            "total_colaboradores": total_colaboradores,
            "total_projetos": total_projetos,
            "contratos_vigentes": contratos_vigentes,
            "alocacoes_ativas": alocacoes_ativas,
            "colaboradores_sem_alocacao": colaboradores_sem_alocacao,
            "total_clientes": Cliente.objects.count(),
            # Alertas
            "contratos_vencendo_30": contratos_vencendo_30.count(),
            "contratos_vencendo_60": contratos_vencendo_60,
            "projetos_sem_contrato": projetos_sem_contrato,
            # Listas
            "projetos_criticos": criticos[:4],
            "projetos_atencao": atencao[:4],
            "projetos_saudaveis": saudaveis[:4],
            "contratos_proximos": contratos_proximos,
            "projetos_recentes": projetos_recentes,
            "colaboradores_recentes": colaboradores_recentes,
            # Gráficos
            "headcount_por_cliente": headcount_por_cliente,
            "alocacoes_por_projeto": alocacoes_por_projeto,
        })
        return ctx

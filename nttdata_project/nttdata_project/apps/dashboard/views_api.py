from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


class DashboardStatsAPIView(APIView):
    """Indicadores gerais para o dashboard."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.colaboradores.models import Colaborador, StatusColaborador, RoleChoices
        from apps.clientes.models import Cliente
        from apps.contratos.models import Contrato
        from apps.projetos.models import Projeto, ColaboradorProjeto
        from apps.notebooks.models import Notebook

        hoje = timezone.now().date()
        primeiro_dia = hoje.replace(day=1)

        # Params de filtro de data
        dt_inicio = request.query_params.get("dt_inicio", str(primeiro_dia))
        dt_fim = request.query_params.get("dt_fim", str(hoje))

        stats = {
            "colaboradores": {
                "total_ativos": Colaborador.objects.filter(status=StatusColaborador.ATIVO, is_active=True).count(),
                "total_inativos": Colaborador.objects.filter(status=StatusColaborador.INATIVO).count(),
                "total_afastados": Colaborador.objects.filter(status=StatusColaborador.AFASTADO).count(),
                "por_role": list(
                    Colaborador.objects.filter(is_active=True)
                    .values("role")
                    .annotate(total=Count("id"))
                    .order_by("role")
                ),
                "por_cidade": list(
                    Colaborador.objects.filter(status=StatusColaborador.ATIVO, cidade__isnull=False)
                    .exclude(cidade="")
                    .values("cidade")
                    .annotate(total=Count("id"))
                    .order_by("-total")[:10]
                ),
                "admitidos_periodo": Colaborador.objects.filter(
                    dt_admissao__gte=dt_inicio, dt_admissao__lte=dt_fim
                ).count(),
            },
            "projetos": {
                "total_ativos": Projeto.objects.filter(ativo=True).count(),
                "total_inativos": Projeto.objects.filter(ativo=False).count(),
                "contrato_pendente": Projeto.objects.filter(ativo=True, contrato_pend=True).count(),
                "por_cliente": list(
                    Projeto.objects.filter(ativo=True)
                    .values("id_cliente__nome")
                    .annotate(total=Count("id"))
                    .order_by("-total")[:8]
                ),
                "alocacoes_ativas": ColaboradorProjeto.objects.filter(dt_fim__isnull=True).count(),
            },
            "clientes": {
                "total": Cliente.objects.count(),
            },
            "contratos": {
                "total_vigentes": Contrato.objects.filter(dt_fim__gte=hoje).count(),
                "vencendo_30_dias": Contrato.objects.filter(
                    dt_fim__gte=hoje, dt_fim__lte=hoje.replace(day=hoje.day + 30) if hoje.day <= 1 else hoje.replace(month=hoje.month + 1 if hoje.month < 12 else 1)
                ).count(),
                "vencidos": Contrato.objects.filter(dt_fim__lt=hoje).count(),
            },
            "notebooks": {
                "total": Notebook.objects.count(),
                "ativos": Notebook.objects.filter(ativo=True).count(),
                "ntt": Notebook.objects.filter(eh_ntt=True).count(),
                "cliente": Notebook.objects.filter(eh_cliente=True).count(),
                "sem_responsavel": Notebook.objects.filter(responsavel__isnull=True, ativo=True).count(),
            },
            "periodo": {"dt_inicio": dt_inicio, "dt_fim": dt_fim},
        }
        return Response(stats)

import csv
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from apps.colaboradores.permissions import IsGerenteOrAbove
from .pdf_utils import build_pdf


# ── Helpers ──────────────────────────────────────────────────────────────────

def _csv_response(filename, headers, rows):
    resp = HttpResponse(content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    resp.write("\ufeff")
    writer = csv.writer(resp, delimiter=";")
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return resp


def _pdf_response(filename, title, subtitle, headers, rows):
    pdf_bytes = build_pdf(title, subtitle, headers, rows, filename)
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


# ── Colaboradores ─────────────────────────────────────────────────────────────

class RelatorioColaboradoresCSV(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.colaboradores.models import Colaborador
        qs = Colaborador.objects.select_related("gestor_direto").filter(is_active=True).order_by("nome")
        headers = ["Nome", "E-mail", "Matrícula", "Cargo", "Função", "Role", "Status", "Cidade", "Estado", "Dt. Admissão", "Gestor"]
        rows = [[c.nome, c.email, c.matricula or "", c.cargo, c.funcao,
                 c.get_role_display(), c.get_status_display(),
                 c.cidade, c.estado, c.dt_admissao or "",
                 c.gestor_direto.nome if c.gestor_direto else ""] for c in qs]
        return _csv_response("colaboradores.csv", headers, rows)


class RelatorioColaboradoresPDF(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.colaboradores.models import Colaborador
        qs = Colaborador.objects.select_related("gestor_direto").filter(is_active=True).order_by("nome")
        headers = ["Nome", "Matrícula", "Cargo", "Função", "Role", "Status", "Cidade/UF", "Dt. Admissão", "Gestor"]
        rows = [[c.nome, c.matricula or "", c.cargo, c.funcao,
                 c.get_role_display(), c.get_status_display(),
                 f"{c.cidade}/{c.estado}" if c.cidade else "",
                 str(c.dt_admissao) if c.dt_admissao else "",
                 c.gestor_direto.nome if c.gestor_direto else ""] for c in qs]
        subtitle = f"Colaboradores ativos — {timezone.localtime(timezone.now()).strftime('%d/%m/%Y')}"
        return _pdf_response("colaboradores.pdf", "Relatório de Colaboradores", subtitle, headers, rows)


# ── Projetos ──────────────────────────────────────────────────────────────────

class RelatorioProjetosCSV(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.projetos.models import Projeto
        qs = Projeto.objects.select_related("id_cliente", "gestor", "contrato").filter(ativo=True)
        headers = ["Projeto", "Cliente", "OV", "Qtd. Prevista", "Qtd. Atual", "% Alocação", "Contrato Pend.", "Gestor"]
        rows = [[p.nome_proj_ntt, p.id_cliente.nome, p.ov, p.qte_pessoas,
                 p.qte_pessoas_atual, f"{p.percentual_alocacao}%",
                 "Sim" if p.contrato_pend else "Não",
                 p.gestor.nome if p.gestor else ""] for p in qs]
        return _csv_response("projetos.csv", headers, rows)


class RelatorioProjetosPDF(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.projetos.models import Projeto
        qs = Projeto.objects.select_related("id_cliente", "gestor", "contrato").filter(ativo=True)
        headers = ["Projeto", "Cliente", "OV", "Prev.", "Atual", "% Aloc.", "Gestor"]
        rows = [[p.nome_proj_ntt, p.id_cliente.nome, p.ov or "", p.qte_pessoas,
                 p.qte_pessoas_atual, f"{p.percentual_alocacao}%",
                 p.gestor.nome if p.gestor else ""] for p in qs]
        subtitle = f"Projetos ativos — {timezone.localtime(timezone.now()).strftime('%d/%m/%Y')}"
        return _pdf_response("projetos.pdf", "Relatório de Projetos", subtitle, headers, rows)


# ── Alocações ─────────────────────────────────────────────────────────────────

class RelatorioAlocacoesCSV(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.projetos.models import ColaboradorProjeto
        qs = ColaboradorProjeto.objects.select_related("id_colaborador", "id_proj", "id_cliente").filter(dt_fim__isnull=True)
        headers = ["Colaborador", "Projeto", "Cliente", "Função", "Squad", "Dt. Início", "Centro de Custo"]
        rows = [[a.id_colaborador.nome, a.nome_proj, a.id_cliente.nome,
                 a.funcao, a.squad, a.dt_inicio, a.centro_custo] for a in qs]
        return _csv_response("alocacoes_ativas.csv", headers, rows)


class RelatorioAlocacoesPDF(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.projetos.models import ColaboradorProjeto, AlocacaoParcial
        from collections import defaultdict
        from .pdf_utils import build_pdf_agrupado

        qs = (ColaboradorProjeto.objects
              .select_related("id_colaborador", "id_proj", "id_cliente")
              .filter(dt_fim__isnull=True)
              .order_by("id_colaborador__nome", "id_proj__nome_proj_ntt"))

        # Agrupa por colaborador
        por_colab = defaultdict(list)
        for a in qs:
            por_colab[a.id_colaborador].append(a)

        # Busca alocações parciais para enriquecer o relatório
        parciais = {
            ap.id_alocacao_id: ap
            for ap in AlocacaoParcial.objects.filter(dt_fim__isnull=True)
                                             .select_related("id_alocacao")
        }

        grupos = []
        for colab, alocacoes in sorted(por_colab.items(), key=lambda x: x[0].nome):
            linhas = []
            for a in alocacoes:
                ap = parciais.get(a.pk)
                horas_str = f"{ap.horas_dia}h/dia ({ap.percentual_dia}%)" if ap else "Integral"
                linhas.append([
                    a.id_proj.nome_proj_ntt,
                    a.id_cliente.nome,
                    a.funcao or "—",
                    a.squad or "—",
                    str(a.dt_inicio) if a.dt_inicio else "—",
                    horas_str,
                ])
            grupos.append({
                "titulo":    colab.nome,
                "subtitulo": f"{colab.cargo}  |  Matrícula: {colab.matricula or '—'}",
                "colunas":   ["Projeto", "Cliente", "Função", "Squad", "Dt. Início", "Dedicação"],
                "linhas":    linhas,
            })

        subtitle = f"Alocações ativas agrupadas por colaborador — {timezone.localtime(timezone.now()).strftime('%d/%m/%Y')}"
        pdf_bytes = build_pdf_agrupado(
            "Relatório de Alocações Ativas", subtitle, grupos, "alocacoes.pdf"
        )
        from django.http import HttpResponse
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = 'attachment; filename="alocacoes.pdf"'
        return resp


# ── Notebooks ─────────────────────────────────────────────────────────────────

class RelatorioNotebooksCSV(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.notebooks.models import Notebook
        qs = Notebook.objects.select_related("responsavel").all()
        headers = ["Nº Série", "Marca", "Modelo", "Origem", "Patrimônio NTT", "Patrimônio Cliente", "Localização", "Responsável", "Ativo"]
        rows = [[n.numero_serie, n.marca, n.modelo, n.origem,
                 n.patrimonio_ntt or "", n.patrimonio_cliente or "",
                 n.localizacao, n.responsavel.nome if n.responsavel else "",
                 "Sim" if n.ativo else "Não"] for n in qs]
        return _csv_response("notebooks.csv", headers, rows)


class RelatorioNotebooksPDF(APIView):
    permission_classes = [IsGerenteOrAbove]

    def get(self, request):
        from apps.notebooks.models import Notebook
        qs = Notebook.objects.select_related("responsavel").all()
        headers = ["Nº Série", "Marca/Modelo", "Origem", "Localização", "Responsável", "Ativo"]
        rows = [[n.numero_serie, f"{n.marca} {n.modelo}".strip(), n.origem,
                 n.localizacao, n.responsavel.nome if n.responsavel else "",
                 "Sim" if n.ativo else "Não"] for n in qs]
        subtitle = f"Inventário de notebooks — {timezone.localtime(timezone.now()).strftime('%d/%m/%Y')}"
        return _pdf_response("notebooks.pdf", "Relatório de Notebooks", subtitle, headers, rows)

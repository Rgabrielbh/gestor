from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Q
import unicodedata


def normalize(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode('ascii').lower().strip()


def fuzzy_qs(qs, fields, q):
    q_norm = normalize(q)
    filtro = Q()
    for f in fields:
        filtro |= Q(**{f"{f}__icontains": q})
    result = qs.filter(filtro).distinct()
    if result.exists():
        return result

    filtro_norm = Q()
    for f in fields:
        filtro_norm |= Q(**{f"{f}__icontains": q_norm})
    result = qs.filter(filtro_norm).distinct()
    if result.exists():
        return result

    ids = []
    for obj in qs:
        for f in fields:
            val = normalize(getattr(obj, f, "") or "")
            if q_norm in val:
                ids.append(obj.pk)
                break
    return qs.filter(pk__in=ids)


def fuzzy_projetos(q):
    from apps.projetos.models import Projeto
    q_norm = normalize(q)
    base = Projeto.objects.select_related("id_cliente").all()

    for filtro in [
        {"nome_proj_ntt__icontains": q},
        {"nome_proj_ntt__icontains": q_norm},
        {"id_cliente__nome__icontains": q},
        {"id_cliente__nome__icontains": q_norm},
    ]:
        qs = base.filter(**filtro)
        if qs.exists():
            return qs

    ids = []
    for p in base:
        nome_proj = normalize(p.nome_proj_ntt)
        nome_cli = normalize(p.id_cliente.nome if p.id_cliente else "")
        if q_norm in nome_proj or q_norm in nome_cli:
            ids.append(p.pk)
    return base.filter(pk__in=ids)


class TimelineIndexView(LoginRequiredMixin, TemplateView):
    template_name = "timeline/index.html"


class TimelineColaboradorView(LoginRequiredMixin, TemplateView):
    template_name = "timeline/colaborador.html"

    def get_context_data(self, **kwargs):
        from apps.colaboradores.models import Colaborador
        from apps.projetos.models import ColaboradorProjeto, AlocacaoParcial

        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        modo = self.request.GET.get("modo", "colaborador")

        ctx.update({"q": q, "modo": modo, "resultado": None,
                    "alocacoes": [], "sugestoes": [], "alocacoes_parciais": []})

        if not q:
            return ctx

        if modo == "colaborador":
            qs = fuzzy_qs(Colaborador.objects.all(), ["nome", "matricula", "cargo"], q)

            if qs.count() == 1:
                colab = qs.first()
                alocacoes = ColaboradorProjeto.objects.filter(
                    id_colaborador=colab
                ).select_related("id_proj", "id_cliente").order_by("dt_inicio")

                # Alocações parciais ativas (divisão de horas)
                parciais_ativas = AlocacaoParcial.objects.filter(
                    id_colaborador=colab, dt_fim__isnull=True
                ).select_related("id_alocacao__id_proj", "id_alocacao__id_cliente")

                ctx.update({
                    "resultado": colab,
                    "alocacoes": alocacoes,
                    "total_projetos": alocacoes.count(),
                    "projeto_atual": alocacoes.filter(dt_fim__isnull=True).first(),
                    "alocacoes_parciais": parciais_ativas,
                    "horas_total": sum(float(a.horas_dia) for a in parciais_ativas),
                })
            elif qs.count() > 1:
                ctx["sugestoes"] = list(qs[:15])

        elif modo == "projeto":
            qs = fuzzy_projetos(q)

            if qs.count() == 1:
                proj = qs.first()
                alocacoes = ColaboradorProjeto.objects.filter(
                    id_proj=proj
                ).select_related("id_colaborador", "id_cliente").order_by("dt_inicio")
                ctx.update({
                    "resultado": proj,
                    "alocacoes": alocacoes,
                    "total_colaboradores": alocacoes.values("id_colaborador").distinct().count(),
                    "alocacoes_ativas": alocacoes.filter(dt_fim__isnull=True).count(),
                })
            elif qs.count() > 1:
                ctx["sugestoes"] = list(qs[:15])

        return ctx


class TimelineNotebookView(LoginRequiredMixin, TemplateView):
    template_name = "timeline/notebook.html"

    def get_context_data(self, **kwargs):
        from apps.notebooks.models import Notebook, NotebookHistorico
        from apps.colaboradores.models import Colaborador
        from apps.clientes.models import Cliente

        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        modo = self.request.GET.get("modo", "notebook")
        dt_inicio_str = self.request.GET.get("dt_inicio", "")
        dt_fim_str = self.request.GET.get("dt_fim", "")

        ctx.update({"q": q, "modo": modo, "dt_inicio": dt_inicio_str,
                    "dt_fim": dt_fim_str, "resultado": None,
                    "historicos": [], "sugestoes": []})

        if not q and modo != "periodo":
            return ctx

        if modo == "notebook" and q:
            qs = fuzzy_qs(
                Notebook.objects.all(),
                ["numero_serie", "modelo", "marca", "patrimonio_ntt",
                 "patrimonio_cliente", "localizacao", "observacoes"], q
            )
            if qs.count() == 1:
                nb = qs.first()
                historicos = NotebookHistorico.objects.filter(
                    notebook=nb
                ).select_related("responsavel", "cliente").order_by("dt_inicio")
                ctx.update({
                    "resultado": nb,
                    "historicos": historicos,
                    "total_responsaveis": historicos.values("responsavel").distinct().count(),
                    "atual": historicos.filter(dt_fim__isnull=True).first(),
                })
            elif qs.count() > 1:
                ctx["sugestoes"] = list(qs[:15])

        elif modo == "colaborador" and q:
            qs = fuzzy_qs(Colaborador.objects.all(), ["nome", "matricula", "cargo"], q)
            if qs.count() == 1:
                colab = qs.first()
                historicos = NotebookHistorico.objects.filter(
                    responsavel=colab
                ).select_related("notebook", "cliente").order_by("dt_inicio")
                ctx.update({"resultado": colab, "historicos": historicos})
            elif qs.count() > 1:
                ctx["sugestoes"] = list(qs[:15])

        elif modo == "cliente" and q:
            qs = fuzzy_qs(Cliente.objects.all(), ["nome", "cnpj"], q)
            if qs.exists():
                historicos = NotebookHistorico.objects.filter(
                    cliente__in=qs
                ).select_related("notebook", "responsavel", "cliente").order_by("dt_inicio")
                ctx["historicos"] = historicos
                if qs.count() == 1:
                    ctx["resultado"] = qs.first()
                else:
                    ctx["resultado"] = "periodo"
                    ctx["sugestoes"] = list(qs[:10])

        elif modo == "periodo" and dt_inicio_str:
            from datetime import date
            try:
                dt_i = date.fromisoformat(dt_inicio_str)
                historicos = NotebookHistorico.objects.filter(dt_inicio__gte=dt_i)
                if dt_fim_str:
                    dt_f = date.fromisoformat(dt_fim_str)
                    historicos = historicos.filter(dt_inicio__lte=dt_f)
                ctx.update({
                    "historicos": historicos.select_related(
                        "notebook", "responsavel", "cliente"
                    ).order_by("dt_inicio"),
                    "resultado": "periodo",
                })
            except ValueError:
                pass

        return ctx

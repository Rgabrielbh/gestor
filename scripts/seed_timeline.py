#!/usr/bin/env python
"""
Seed de dados históricos para Timeline + AlocacaoParcial.
Rode APÓS seed_data.py e migrations.

    docker compose exec web python scripts/seed_timeline.py
"""
import os, sys, django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from decimal import Decimal
from datetime import date
from apps.colaboradores.models import Colaborador
from apps.clientes.models import Cliente
from apps.projetos.models import Projeto, ColaboradorProjeto, AlocacaoParcial
from apps.notebooks.models import Notebook, NotebookHistorico

def log(msg): print(f"  ✓ {msg}")
def warn(msg): print(f"  ⚠ {msg}")

def get(model, **kw):
    try:
        return model.objects.get(**kw)
    except model.DoesNotExist:
        return None


def seed_historico_notebooks():
    print("\n[1/3] Populando histórico de notebooks...")
    NotebookHistorico.objects.all().delete()

    itau    = get(Cliente, nome__icontains="Itaú")
    petro   = get(Cliente, nome__icontains="Petrobras")
    magalu  = get(Cliente, nome__icontains="Magazine")

    historicos = {
        "NB-NTT-001": [
            ("thiago.qa",    None,  "São Paulo — Escritório",       date(2022,1,10), date(2022,8,31), "Entregue na admissão"),
            ("fernanda.dev", None,  "São Paulo — Escritório",       date(2022,9, 1), date(2023,4,30), "Troca de projeto"),
            ("lucas.dev",    None,  "São Paulo — Escritório",       date(2023,5, 1), None,            "Responsável atual"),
        ],
        "NB-NTT-002": [
            ("rafael.devops",None,  "Rio de Janeiro — Escritório",  date(2022,3, 1), date(2023,2,28), "Projeto Petrobras"),
            ("fernanda.dev", None,  "São Paulo — Escritório",       date(2023,3, 1), None,            "Responsável atual"),
        ],
        "NB-NTT-003": [
            ("vitor.back",   None,  "São Paulo — Home Office",      date(2022,6, 1), date(2023,5,31), "Home office"),
            ("thiago.qa",    None,  "São Paulo — Home Office",      date(2023,6, 1), None,            "Responsável atual"),
        ],
        "NB-NTT-004": [
            ("camila.ba",    None,  "Rio de Janeiro — Escritório",  date(2022,2, 1), date(2022,11,30),"Admissão"),
            ("pedro.arch",   None,  "Rio de Janeiro — Escritório",  date(2022,12,1), date(2023,8,31), "Troca de equipe"),
            ("rafael.devops",None,  "Rio de Janeiro — Escritório",  date(2023,9, 1), None,            "Responsável atual"),
        ],
        "NB-NTT-005": [
            ("diego.cloud",  None,  "Rio de Janeiro — Escritório",  date(2022,4, 1), date(2023,3,31), "Projeto Cloud"),
            ("camila.ba",    None,  "Rio de Janeiro — Home Office", date(2023,4, 1), None,            "Responsável atual"),
        ],
        "NB-CLI-001": [
            ("pedro.arch",   itau,  "Itaú — Paulista",              date(2022,8, 1), date(2023,7,31), "Fase 1"),
            ("vitor.back",   itau,  "Itaú — Paulista",              date(2023,8, 1), date(2024,1,31), "Fase 2"),
            ("pedro.arch",   itau,  "Itaú — Paulista",              date(2024,2, 1), None,            "Retorno atual"),
        ],
        "NB-CLI-002": [
            ("rafael.devops",petro, "Petrobras — Rio",              date(2022,10,1), date(2023,9,30), "E&P fase 1"),
            ("isabela.data", petro, "Petrobras — Rio",              date(2023,10,1), None,            "Responsável atual"),
        ],
        "NB-CLI-003": [
            ("gabriel.mobile",magalu,"Magalu — Franca",             date(2023,1, 1), date(2023,6,30), "E-commerce sprint"),
            ("juliana.ux",   magalu, "Magalu — Franca",             date(2023,7, 1), None,            "Responsável atual"),
        ],
        "NB-NTT-006": [("ana.gestora",  None, "São Paulo — Escritório",       date(2021,6,1), None, "Gestor")],
        "NB-NTT-007": [("carlos.gestor",None, "Rio de Janeiro — Escritório",  date(2021,6,1), None, "Gestor")],
    }

    for serie, registros in historicos.items():
        nb = get(Notebook, numero_serie=serie)
        if not nb:
            warn(f"Notebook não encontrado: {serie}")
            continue
        for username, cliente_obj, loc, dt_i, dt_f, obs in registros:
            NotebookHistorico.objects.create(
                notebook=nb, responsavel=get(Colaborador, username=username),
                cliente=cliente_obj, localizacao=loc,
                dt_inicio=dt_i, dt_fim=dt_f, observacao=obs,
            )
        log(f"{serie} — {len(registros)} registro(s)")


def seed_historico_alocacoes():
    print("\n[2/3] Criando alocações históricas encerradas...")
    ColaboradorProjeto.objects.filter(dt_fim__isnull=False).delete()

    projetos = list(Projeto.objects.filter(ativo=True).select_related("id_cliente").order_by("id"))
    if not projetos:
        warn("Nenhum projeto. Rode seed_data.py primeiro.")
        return

    def p(i): return projetos[i % len(projetos)]

    extras = [
        ("lucas.dev",      2, "Dev Backend",       "Squad E&P",      "CC-003", date(2021,6, 1), date(2022,11,30)),
        ("lucas.dev",      3, "Dev Full Stack",    "Squad Digital",  "CC-004", date(2022,12,1), date(2023,7, 31)),
        ("fernanda.dev",   4, "Dev Frontend",      "Squad Indústria","CC-005", date(2021,3, 1), date(2023,2, 28)),
        ("fernanda.dev",   2, "Dev Frontend",      "Squad E&P",      "CC-003", date(2023,3, 1), date(2023,12,31)),
        ("thiago.qa",      4, "QA Lead",           "Squad Indústria","CC-005", date(2021,1, 1), date(2023,6, 30)),
        ("thiago.qa",      1, "QA Senior",         "Core Team",      "CC-002", date(2023,7, 1), date(2023,12,31)),
        ("rafael.devops",  0, "DevOps Engineer",   "Squad Alpha",    "CC-001", date(2021,8, 1), date(2023,7, 31)),
        ("rafael.devops",  3, "Cloud Ops",         "Squad Digital",  "CC-004", date(2023,8, 1), date(2024,1, 31)),
        ("camila.ba",      1, "Business Analyst",  "Core Team",      "CC-002", date(2021,6, 1), date(2022,11,30)),
        ("camila.ba",      3, "Business Analyst",  "Squad Digital",  "CC-004", date(2022,12,1), date(2023,11,30)),
        ("pedro.arch",     0, "Arquiteto Jr",      "Squad Alpha",    "CC-001", date(2020,5, 1), date(2021,4, 30)),
        ("pedro.arch",     0, "Arquiteto Pleno",   "Squad Alpha",    "CC-001", date(2021,5, 1), date(2022,8, 31)),
        ("pedro.arch",     1, "Arquiteto Sênior",  "Core Team",      "CC-002", date(2022,9, 1), date(2023,8, 31)),
        ("vitor.back",     2, "Backend Developer", "Squad E&P",      "CC-003", date(2021,2, 1), date(2023,6, 30)),
        ("vitor.back",     3, "Backend Senior",    "Squad Digital",  "CC-004", date(2023,7, 1), date(2023,12,31)),
        ("larissa.front",  4, "Frontend Dev",      "Squad Indústria","CC-005", date(2021,7, 1), date(2023,6, 30)),
        ("larissa.front",  3, "Frontend Senior",   "Squad Digital",  "CC-004", date(2023,7, 1), date(2023,12,31)),
        ("isabela.data",   3, "Data Analyst",      "Squad Digital",  "CC-004", date(2021,9, 1), date(2023,8, 31)),
        ("gabriel.mobile", 1, "Mobile Dev",        "Core Team",      "CC-002", date(2021,6, 1), date(2022,11,30)),
        ("gabriel.mobile", 3, "Mobile Senior",     "Squad Digital",  "CC-004", date(2022,12,1), date(2023,7, 31)),
        ("amanda.scrum",   2, "Scrum Master",      "Squad E&P",      "CC-003", date(2021,4, 1), date(2023,3, 31)),
        ("henrique.sec",   3, "Security Analyst",  "Squad Digital",  "CC-004", date(2021,8, 1), date(2023,7, 31)),
        ("diego.cloud",    0, "Cloud Architect",   "Squad Alpha",    "CC-001", date(2020,10,1), date(2022,9, 30)),
        ("diego.cloud",    2, "Cloud Senior",      "Squad E&P",      "CC-003", date(2022,10,1), date(2023,11,30)),
        ("natalia.pm",     2, "Product Owner",     "Squad E&P",      "CC-003", date(2021,6, 1), date(2023,5, 31)),
        ("juliana.ux",     0, "UX Designer",       "Squad Alpha",    "CC-001", date(2021,6, 1), date(2022,11,30)),
        ("juliana.ux",     1, "UX Senior",         "Core Team",      "CC-002", date(2022,12,1), date(2023,6, 30)),
    ]

    criados = 0
    for username, proj_idx, funcao, squad, cc, dt_inicio, dt_fim in extras:
        colab = get(Colaborador, username=username)
        if not colab:
            warn(f"Colaborador não encontrado: {username}")
            continue
        proj = p(proj_idx)
        _, created = ColaboradorProjeto.objects.get_or_create(
            id_proj=proj, id_colaborador=colab, dt_inicio=dt_inicio,
            defaults=dict(id_cliente=proj.id_cliente, funcao=funcao,
                          squad=squad, centro_custo=cc, dt_fim=dt_fim,
                          contato_projeto="projetos@nttdata.com")
        )
        if created:
            d = (dt_fim - dt_inicio).days
            log(f"{colab.nome:25} → {proj.nome_proj_ntt[:30]:30} [{d//365}a {(d%365)//30}m]")
            criados += 1
    print(f"  Total: {criados} alocações históricas")


def seed_alocacoes_parciais():
    """Colaboradores alocados em 2 projetos simultaneamente com divisão de horas."""
    print("\n[3/3] Criando alocações parciais (divisão de horas por dia)...")
    AlocacaoParcial.objects.all().delete()

    projetos = list(Projeto.objects.filter(ativo=True).select_related("id_cliente").order_by("id"))
    if len(projetos) < 2:
        warn("Projetos insuficientes.")
        return

    def p(i): return projetos[i % len(projetos)]

    # (username, proj_idx_a, horas_a, proj_idx_b, horas_b, descricao)
    parciais = [
        # Fábio: manhã no Itaú (3h), tarde no Magalu (5h)
        ("lucas.dev",       0, Decimal("3.0"), 3, Decimal("5.0"),
         "Manhã: Itaú Open Banking | Tarde: Magalu Digital"),
        # Fernanda: 50/50
        ("fernanda.dev",    0, Decimal("4.0"), 2, Decimal("4.0"),
         "Meio período em cada projeto"),
        # Thiago: 6h no principal, 2h suporte
        ("thiago.qa",       0, Decimal("6.0"), 1, Decimal("2.0"),
         "Foco no Itaú + suporte QA Core Banking"),
        # Rafael: 5h devops + 3h cloud
        ("rafael.devops",   4, Decimal("5.0"), 0, Decimal("3.0"),
         "Embraer manhã + suporte cloud Itaú tarde"),
        # Pedro: arquitetura dividida
        ("pedro.arch",      2, Decimal("4.0"), 1, Decimal("4.0"),
         "Petrobras e Itaú Core — arquitetura compartilhada"),
        # Camila: 60% num projeto, 40% noutro
        ("camila.ba",       3, Decimal("5.0"), 4, Decimal("3.0"),
         "Foco Magalu + apoio Embraer"),
    ]

    criados = 0
    for username, idx_a, horas_a, idx_b, horas_b, obs in parciais:
        colab = get(Colaborador, username=username)
        if not colab:
            warn(f"Colaborador não encontrado: {username}")
            continue

        proj_a = p(idx_a)
        proj_b = p(idx_b)

        # Buscar ou criar a alocação ativa no projeto A
        aloc_a = ColaboradorProjeto.objects.filter(
            id_colaborador=colab, id_proj=proj_a, dt_fim__isnull=True
        ).first()
        if not aloc_a:
            aloc_a, _ = ColaboradorProjeto.objects.get_or_create(
                id_colaborador=colab, id_proj=proj_a, dt_fim__isnull=True,
                defaults=dict(id_cliente=proj_a.id_cliente,
                              dt_inicio=date(2024, 1, 1), funcao="Desenvolvedor")
            )

        aloc_b = ColaboradorProjeto.objects.filter(
            id_colaborador=colab, id_proj=proj_b, dt_fim__isnull=True
        ).first()
        if not aloc_b:
            aloc_b, _ = ColaboradorProjeto.objects.get_or_create(
                id_colaborador=colab, id_proj=proj_b, dt_fim__isnull=True,
                defaults=dict(id_cliente=proj_b.id_cliente,
                              dt_inicio=date(2024, 6, 1), funcao="Desenvolvedor")
            )

        AlocacaoParcial.objects.create(
            id_colaborador=colab, id_alocacao=aloc_a,
            horas_dia=horas_a, dt_inicio=date(2024, 6, 1),
            observacao=obs,
        )
        AlocacaoParcial.objects.create(
            id_colaborador=colab, id_alocacao=aloc_b,
            horas_dia=horas_b, dt_inicio=date(2024, 6, 1),
            observacao=obs,
        )
        log(f"{colab.nome:25} → {proj_a.nome_proj_ntt[:22]:22} ({horas_a}h) + "
            f"{proj_b.nome_proj_ntt[:22]:22} ({horas_b}h) = {horas_a+horas_b}h/dia")
        criados += 1

    print(f"  Total: {criados} colaboradores com alocação parcial")


def main():
    print("=" * 62)
    print("  NTT Data — Seed de Timeline + Alocações Parciais")
    print("=" * 62)
    seed_historico_notebooks()
    seed_historico_alocacoes()
    seed_alocacoes_parciais()
    print("\n" + "=" * 62)
    print(f"  NotebookHistorico  : {NotebookHistorico.objects.count()}")
    print(f"  Alocações total    : {ColaboradorProjeto.objects.count()}")
    print(f"  Alocações ativas   : {ColaboradorProjeto.objects.filter(dt_fim__isnull=True).count()}")
    print(f"  Alocações hist.    : {ColaboradorProjeto.objects.filter(dt_fim__isnull=False).count()}")
    print(f"  Alocações parciais : {AlocacaoParcial.objects.count()}")
    print("=" * 62)
    print("\n  Exemplos com divisão de horas:")
    print("  Timeline → Lucas Rodrigues   (3h Itaú + 5h Magalu)")
    print("  Timeline → Fernanda Costa    (4h + 4h)")
    print("  Timeline → Pedro H. Lima     (4h Petrobras + 4h Itaú Core)")
    print("=" * 62)

if __name__ == "__main__":
    main()

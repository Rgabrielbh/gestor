#!/usr/bin/env python
"""
Script para popular o banco com dados de teste.

Uso dentro do container Docker:
    docker compose exec web python scripts/seed_data.py
"""
import os, sys, django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from apps.colaboradores.models import Colaborador, RoleChoices, StatusColaborador
from apps.clientes.models import Cliente
from apps.contratos.models import Contrato
from apps.projetos.models import Projeto, ColaboradorProjeto
from apps.notebooks.models import Notebook


def log(msg): print(f"  ✓ {msg}")


def criar_colaboradores():
    print("\n[1/5] Criando colaboradores...")

    diretor, c = Colaborador.objects.get_or_create(
        username="joao.diretor",
        defaults=dict(email="joao.diretor@nttdata.com", nome="João Carlos Silva",
                      role=RoleChoices.DIRETOR, cargo="Diretor de Operações",
                      funcao="Gestão Estratégica", cidade="São Paulo", estado="SP",
                      matricula="D001", dt_admissao=date(2018, 3, 15),
                      salario=Decimal("28000.00"), status=StatusColaborador.ATIVO)
    )
    if c: diretor.set_password("Ntt@2024!"); diretor.save(); log(f"{diretor.nome} [Diretor]")

    gestores = []
    for username, nome, mat, cidade, estado in [
        ("ana.gestora",   "Ana Paula Ferreira",  "G001", "São Paulo",     "SP"),
        ("carlos.gestor", "Carlos Eduardo Lima", "G002", "Rio de Janeiro", "RJ"),
    ]:
        g, c = Colaborador.objects.get_or_create(
            username=username,
            defaults=dict(email=f"{username}@nttdata.com", nome=nome,
                          role=RoleChoices.GESTOR, cargo="Gestor de Projetos",
                          funcao="Gestão", cidade=cidade, estado=estado,
                          matricula=mat, dt_admissao=date(2019, 6, 1),
                          salario=Decimal("18000.00"), gestor_direto=diretor,
                          status=StatusColaborador.ATIVO)
        )
        if c: g.set_password("Ntt@2024!"); g.save(); log(f"{g.nome} [Gestor]")
        gestores.append(g)

    operadores = []
    ops_data = [
        ("lucas.dev",      "Lucas Rodrigues",      "O001", "São Paulo",     "SP", "Desenvolvedor Sênior",  gestores[0]),
        ("fernanda.dev",   "Fernanda Costa",       "O002", "São Paulo",     "SP", "Desenvolvedora Pleno",  gestores[0]),
        ("thiago.qa",      "Thiago Barbosa",       "O003", "Campinas",      "SP", "Analista QA",           gestores[0]),
        ("juliana.ux",     "Juliana Nascimento",   "O004", "São Paulo",     "SP", "UX Designer",           gestores[0]),
        ("rafael.devops",  "Rafael Santos",        "O005", "Rio de Janeiro","RJ", "DevOps Engineer",       gestores[1]),
        ("camila.ba",      "Camila Pereira",       "O006", "Rio de Janeiro","RJ", "Business Analyst",      gestores[1]),
        ("pedro.arch",     "Pedro Henrique Lima",  "O007", "Rio de Janeiro","RJ", "Arquiteto de Soluções", gestores[1]),
        ("amanda.scrum",   "Amanda Vieira",        "O008", "Belo Horizonte","MG", "Scrum Master",          gestores[0]),
        ("gabriel.mobile", "Gabriel Carvalho",     "O009", "São Paulo",     "SP", "Dev Mobile",            gestores[0]),
        ("isabela.data",   "Isabela Martins",      "O010", "Curitiba",      "PR", "Data Engineer",         gestores[1]),
        ("vitor.back",     "Vitor Souza",          "O011", "São Paulo",     "SP", "Backend Developer",     gestores[0]),
        ("larissa.front",  "Larissa Gomes",        "O012", "São Paulo",     "SP", "Frontend Developer",    gestores[0]),
        ("diego.cloud",    "Diego Ribeiro",        "O013", "Rio de Janeiro","RJ", "Cloud Architect",       gestores[1]),
        ("natalia.pm",     "Natalia Fernandes",    "O014", "Brasília",      "DF", "Product Manager",       gestores[1]),
        ("henrique.sec",   "Henrique Alves",       "O015", "São Paulo",     "SP", "Security Engineer",     gestores[0]),
    ]
    for username, nome, mat, cidade, estado, cargo, gestor in ops_data:
        op, c = Colaborador.objects.get_or_create(
            username=username,
            defaults=dict(email=f"{username}@nttdata.com", nome=nome,
                          role=RoleChoices.OPERADOR, cargo=cargo, funcao=cargo,
                          cidade=cidade, estado=estado, matricula=mat,
                          dt_admissao=date(2022, 4, 1), salario=Decimal("8500.00"),
                          gestor_direto=gestor, status=StatusColaborador.ATIVO)
        )
        if c: op.set_password("Ntt@2024!"); op.save(); log(f"{op.nome} [Operador]")
        operadores.append(op)

    return diretor, gestores, operadores


def criar_clientes():
    print("\n[2/5] Criando clientes...")
    clientes = []
    for cnpj, nome, resp in [
        ("12.345.678/0001-90", "Banco Itaú S.A.",     "Ana Paula Ferreira"),
        ("23.456.789/0001-01", "Petrobras S.A.",       "Carlos Eduardo Lima"),
        ("34.567.890/0001-12", "Magazine Luiza S.A.", "Ana Paula Ferreira"),
        ("45.678.901/0001-23", "Embraer S.A.",         "Carlos Eduardo Lima"),
    ]:
        c, created = Cliente.objects.get_or_create(cnpj=cnpj, defaults=dict(nome=nome, resp_nttdata=resp))
        if created: log(f"{c.nome}")
        clientes.append(c)
    return clientes


def criar_contratos(clientes):
    print("\n[3/5] Criando contratos...")
    hoje = date.today()
    contratos = []
    for cliente, codigo, descricao, fte, inicio, fim, renova in [
        (clientes[0], "CTR-2023-001", "Transformação Digital Bancária",  15, date(2023,1,1),  hoje+timedelta(days=180), True),
        (clientes[0], "CTR-2024-002", "Modernização de Sistemas Core",    8, date(2024,3,1),  hoje+timedelta(days=365), False),
        (clientes[1], "CTR-2023-003", "Plataforma de E&P Digital",       12, date(2023,6,1),  hoje+timedelta(days=90),  True),
        (clientes[2], "CTR-2024-004", "E-commerce e Jornada do Cliente",  6, date(2024,1,15), hoje+timedelta(days=270), False),
        (clientes[3], "CTR-2022-005", "Indústria 4.0 — Automação",       10, date(2022,9,1),  hoje-timedelta(days=30),  True),
    ]:
        ct, created = Contrato.objects.get_or_create(
            codigo=codigo,
            defaults=dict(descricao=descricao, cliente=cliente, fte=fte,
                          dt_inicio=inicio, dt_fim=fim, renova=renova,
                          ov_anterior=f"OV-{codigo[-3:]}", resp_cliente=f"Resp. {cliente.nome[:20]}")
        )
        if created: log(f"{ct.codigo} — {ct.descricao[:40]}")
        contratos.append(ct)
    return contratos


def criar_projetos(clientes, contratos, gestores, operadores):
    print("\n[4/5] Criando projetos e alocações...")

    projetos_spec = [
        (clientes[0], contratos[0], "Banco Itaú — Open Banking",       "OV-P001", 5, gestores[0]),
        (clientes[0], contratos[1], "Banco Itaú — Core Banking",       "OV-P002", 4, gestores[0]),
        (clientes[1], contratos[2], "Petrobras — Plataforma E&P",      "OV-P003", 6, gestores[1]),
        (clientes[2], contratos[3], "Magalu — Jornada Digital",        "OV-P004", 3, gestores[0]),
        (clientes[3], contratos[4], "Embraer — Automação Industrial",  "OV-P005", 4, gestores[1]),
    ]
    alocacoes_spec = [
        (0, operadores[0],  "Dev Backend",      "Squad Alpha",  "CC-001"),
        (0, operadores[1],  "Dev Frontend",     "Squad Alpha",  "CC-001"),
        (0, operadores[2],  "QA Analyst",       "Squad Alpha",  "CC-001"),
        (0, operadores[8],  "Dev Mobile",       "Squad Beta",   "CC-001"),
        (1, operadores[10], "Dev Backend",      "Core Team",    "CC-002"),
        (1, operadores[11], "Dev Frontend",     "Core Team",    "CC-002"),
        (2, operadores[4],  "DevOps",           "Infra Squad",  "CC-003"),
        (2, operadores[6],  "Arquiteto",        "Infra Squad",  "CC-003"),
        (2, operadores[9],  "Data Engineer",    "Data Squad",   "CC-003"),
        (2, operadores[14], "Security Eng.",    "Sec Squad",    "CC-003"),
        (3, operadores[3],  "UX Designer",      "Digital Squad","CC-004"),
        (3, operadores[5],  "Business Analyst", "Digital Squad","CC-004"),
        (4, operadores[12], "Cloud Architect",  "Cloud Team",   "CC-005"),
        (4, operadores[13], "Product Manager",  "Cloud Team",   "CC-005"),
        (4, operadores[7],  "Scrum Master",     "Cloud Team",   "CC-005"),
    ]

    projetos = []
    for idx, (cliente, contrato, nome, ov, qte, gestor) in enumerate(projetos_spec):
        n_aloc = sum(1 for a in alocacoes_spec if a[0] == idx)
        p, created = Projeto.objects.get_or_create(
            nome_proj_ntt=nome,
            defaults=dict(id_cliente=cliente, contrato=contrato, ov=ov,
                          qte_pessoas=qte, qte_pessoas_atual=n_aloc,
                          gestor=gestor, ativo=True, contrato_pend=False)
        )
        if created: log(f"Projeto: {p.nome_proj_ntt}")
        projetos.append(p)

    for proj_idx, colab, funcao, squad, cc in alocacoes_spec:
        proj = projetos[proj_idx]
        aloc, created = ColaboradorProjeto.objects.get_or_create(
            id_proj=proj, id_colaborador=colab,
            defaults=dict(id_cliente=proj.id_cliente, funcao=funcao, squad=squad,
                          centro_custo=cc, dt_inicio=date(2024, 1, 1),
                          contato_projeto="projetos@nttdata.com",
                          resp_cliente=f"Resp. {proj.id_cliente.nome[:15]}")
        )
        if created: log(f"  Alocado: {colab.nome} → {proj.nome_proj_ntt}")

    return projetos


def criar_notebooks(operadores, gestores):
    print("\n[5/5] Criando notebooks...")
    for serie, eh_ntt, pat_ntt, eh_cli, pat_cli, loc, resp, marca, modelo in [
        ("NB-NTT-001", True,  "NTT-0001", False, None,       "São Paulo — Escritório",      operadores[0],  "Dell",   "Latitude 5530"),
        ("NB-NTT-002", True,  "NTT-0002", False, None,       "São Paulo — Escritório",      operadores[1],  "Lenovo", "ThinkPad T14"),
        ("NB-NTT-003", True,  "NTT-0003", False, None,       "São Paulo — Home Office",     operadores[2],  "HP",     "EliteBook 840"),
        ("NB-NTT-004", True,  "NTT-0004", False, None,       "Rio de Janeiro — Escritório", operadores[4],  "Dell",   "Latitude 7430"),
        ("NB-NTT-005", True,  "NTT-0005", False, None,       "Rio de Janeiro — HO",         operadores[5],  "Apple",  "MacBook Pro 14"),
        ("NB-CLI-001", False, None,        True,  "CLI-1001", "Itaú — Paulista",             operadores[6],  "Apple",  "MacBook Air M2"),
        ("NB-CLI-002", False, None,        True,  "CLI-1002", "Petrobras — Rio",             operadores[9],  "Dell",   "XPS 15"),
        ("NB-CLI-003", False, None,        True,  "CLI-1003", "Magalu — Franca",             operadores[3],  "Lenovo", "ThinkPad X1 Carbon"),
        ("NB-NTT-006", True,  "NTT-0006", False, None,       "São Paulo — Escritório",      gestores[0],    "Apple",  "MacBook Pro 16"),
        ("NB-NTT-007", True,  "NTT-0007", False, None,       "Rio de Janeiro — Escritório", gestores[1],    "Apple",  "MacBook Pro 16"),
    ]:
        nb, created = Notebook.objects.get_or_create(
            numero_serie=serie,
            defaults=dict(eh_ntt=eh_ntt, patrimonio_ntt=pat_ntt,
                          eh_cliente=eh_cli, patrimonio_cliente=pat_cli,
                          localizacao=loc, responsavel=resp,
                          marca=marca, modelo=modelo, ativo=True)
        )
        if created: log(f"{nb.numero_serie} — {nb.marca} {nb.modelo} ({nb.origem})")


def main():
    print("=" * 55)
    print("  NTT Data — Seed de Dados de Teste")
    print("=" * 55)

    diretor, gestores, operadores = criar_colaboradores()
    clientes  = criar_clientes()
    contratos = criar_contratos(clientes)
    criar_projetos(clientes, contratos, gestores, operadores)
    criar_notebooks(operadores, gestores)

    print("\n" + "=" * 55)
    print("  Resumo final:")
    print(f"  Colaboradores : {Colaborador.objects.count()}")
    print(f"  Clientes      : {Cliente.objects.count()}")
    print(f"  Contratos     : {Contrato.objects.count()}")
    print(f"  Projetos      : {Projeto.objects.count()}")
    print(f"  Alocações     : {ColaboradorProjeto.objects.count()}")
    print(f"  Notebooks     : {Notebook.objects.count()}")
    print("=" * 55)
    print("\n  Credenciais de acesso:")
    print("  Diretor  → joao.diretor   / Ntt@2024!")
    print("  Gestor   → ana.gestora    / Ntt@2024!")
    print("  Gestor   → carlos.gestor  / Ntt@2024!")
    print("  Operador → lucas.dev      / Ntt@2024!")
    print("=" * 55)


if __name__ == "__main__":
    main()

"""Testes unitários — Models (≥98% de acurácia)."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.colaboradores.models import Colaborador, RoleChoices, StatusColaborador


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_colaborador(**kwargs):
    defaults = dict(username="test1", email="test1@nttdata.com",
                    nome="Test User", role=RoleChoices.OPERADOR)
    defaults.update(kwargs)
    u = Colaborador(**defaults)
    u.set_password("Senha@123")
    u.save()
    return u


def make_cliente(nome="Cliente Teste", cnpj="00.000.000/0001-00"):
    from apps.clientes.models import Cliente
    return Cliente.objects.create(nome=nome, cnpj=cnpj)


def make_contrato(cliente, dias=365):
    from apps.contratos.models import Contrato
    hoje = date.today()
    return Contrato.objects.create(
        cliente=cliente,
        codigo=f"CT-{cliente.pk}",
        dt_inicio=hoje,
        dt_fim=hoje + timedelta(days=dias),
    )


def make_projeto(cliente, contrato=None, nome="Projeto Teste"):
    from apps.projetos.models import Projeto
    return Projeto.objects.create(
        nome_proj_ntt=nome,
        id_cliente=cliente,
        contrato=contrato,
        qte_pessoas=5,
        qte_pessoas_atual=3,
    )


def make_alocacao(colaborador, projeto, dt_inicio=None, dt_fim=None, funcao="Dev"):
    from apps.projetos.models import ColaboradorProjeto
    if dt_inicio is None:
        dt_inicio = date.today() - timedelta(days=30)
    return ColaboradorProjeto.objects.create(
        id_proj=projeto,
        id_colaborador=colaborador,
        id_cliente=projeto.id_cliente,
        dt_inicio=dt_inicio,
        dt_fim=dt_fim,
        funcao=funcao,
    )


# ── Colaborador ───────────────────────────────────────────────────────────────

class ColaboradorModelTests(TestCase):
    def test_operador_nao_is_staff(self):
        u = make_colaborador()
        self.assertFalse(u.is_staff)

    def test_diretor_sets_is_staff(self):
        u = make_colaborador(username="d1", email="d1@nttdata.com", role=RoleChoices.DIRETOR)
        self.assertTrue(u.is_staff)

    def test_gestor_sets_is_staff(self):
        u = make_colaborador(username="g1", email="g1@nttdata.com", role=RoleChoices.GESTOR)
        self.assertTrue(u.is_staff)

    def test_nome_splits_to_first_last(self):
        u = make_colaborador(nome="Maria Silva")
        self.assertEqual(u.first_name, "Maria")
        self.assertEqual(u.last_name, "Silva")

    def test_str_contains_nome(self):
        u = make_colaborador()
        self.assertIn("Test User", str(u))

    def test_is_diretor_property(self):
        u = make_colaborador(username="d2", email="d2@nttdata.com", role=RoleChoices.DIRETOR)
        self.assertTrue(u.is_diretor)

    def test_nao_diretor(self):
        u = make_colaborador()
        self.assertFalse(u.is_diretor)

    def test_email_unique(self):
        make_colaborador()
        with self.assertRaises(Exception):
            make_colaborador(username="outro")

    def test_check_password(self):
        u = make_colaborador()
        self.assertTrue(u.check_password("Senha@123"))
        self.assertFalse(u.check_password("errada"))

    def test_gestor_direto(self):
        gestor = make_colaborador(username="g2", email="g2@nttdata.com", role=RoleChoices.GESTOR)
        sub = make_colaborador(username="s1", email="s1@nttdata.com", gestor_direto=gestor)
        self.assertEqual(sub.gestor_direto, gestor)

    def test_status_padrao_ativo(self):
        u = make_colaborador()
        self.assertEqual(u.status, StatusColaborador.ATIVO)

    def test_status_inativo(self):
        u = make_colaborador(status=StatusColaborador.INATIVO)
        self.assertEqual(u.status, StatusColaborador.INATIVO)


# ── Projeto / ColaboradorProjeto ──────────────────────────────────────────────

class ProjetoModelTests(TestCase):
    def setUp(self):
        self.cliente = make_cliente()
        self.proj = make_projeto(self.cliente)

    def test_percentual_alocacao(self):
        self.assertEqual(self.proj.percentual_alocacao, 60.0)

    def test_percentual_zero_quando_sem_previsao(self):
        p = make_projeto(self.cliente, nome="P2")
        p.qte_pessoas = 0
        p.save()
        self.assertEqual(p.percentual_alocacao, 0)

    def test_str_projeto(self):
        self.assertIn("Projeto Teste", str(self.proj))


class ColaboradorProjetoTests(TestCase):
    def setUp(self):
        self.cliente = make_cliente()
        self.proj = make_projeto(self.cliente)
        self.colab = make_colaborador()

    def test_alocacao_ativa(self):
        aloc = make_alocacao(self.colab, self.proj)
        self.assertTrue(aloc.ativo)

    def test_alocacao_encerrada(self):
        aloc = make_alocacao(self.colab, self.proj,
                              dt_fim=date.today() - timedelta(days=1))
        self.assertFalse(aloc.ativo)

    def test_duracao_retorna_string(self):
        aloc = make_alocacao(self.colab, self.proj,
                              dt_inicio=date.today() - timedelta(days=400))
        self.assertIn("ano", aloc.duracao)

    def test_duracao_dias(self):
        aloc = make_alocacao(self.colab, self.proj,
                              dt_inicio=date.today() - timedelta(days=10))
        self.assertIn("dia", aloc.duracao)


# ── AlocacaoParcial ───────────────────────────────────────────────────────────

class AlocacaoParcialTests(TestCase):
    def setUp(self):
        self.cliente1 = make_cliente(nome="Itaú", cnpj="11.111.111/0001-11")
        self.cliente2 = make_cliente(nome="Magalu", cnpj="22.222.222/0001-22")
        self.proj1 = make_projeto(self.cliente1, nome="Proj Itaú")
        self.proj2 = make_projeto(self.cliente2, nome="Proj Magalu")
        self.colab = make_colaborador()
        self.aloc1 = make_alocacao(self.colab, self.proj1)
        self.aloc2 = make_alocacao(self.colab, self.proj2)

    def _make_parcial(self, alocacao, horas, dt_fim=None):
        from apps.projetos.models import AlocacaoParcial
        return AlocacaoParcial(
            id_colaborador=self.colab,
            id_alocacao=alocacao,
            horas_dia=Decimal(str(horas)),
            dt_inicio=date.today(),
            dt_fim=dt_fim,
        )

    def test_parcial_valida_4h(self):
        ap = self._make_parcial(self.aloc1, 4)
        ap.save()  # não deve lançar exceção
        self.assertEqual(float(ap.horas_dia), 4.0)

    def test_parcial_8h_integral(self):
        ap = self._make_parcial(self.aloc1, 8)
        ap.save()
        self.assertEqual(float(ap.horas_dia), 8.0)

    def test_parcial_excede_8h_lanca_erro(self):
        from apps.projetos.models import AlocacaoParcial
        AlocacaoParcial.objects.create(
            id_colaborador=self.colab, id_alocacao=self.aloc1,
            horas_dia=Decimal("5.0"), dt_inicio=date.today(),
        )
        ap = self._make_parcial(self.aloc2, 4)  # 5 + 4 = 9 > 8
        with self.assertRaises(ValidationError):
            ap.save()

    def test_parcial_dois_projetos_8h_exato(self):
        from apps.projetos.models import AlocacaoParcial
        AlocacaoParcial.objects.create(
            id_colaborador=self.colab, id_alocacao=self.aloc1,
            horas_dia=Decimal("4.0"), dt_inicio=date.today(),
        )
        ap2 = self._make_parcial(self.aloc2, 4)
        ap2.save()  # 4 + 4 = 8 — OK
        self.assertTrue(True)

    def test_percentual_dia(self):
        ap = self._make_parcial(self.aloc1, 4)
        ap.save()
        self.assertEqual(ap.percentual_dia, 50.0)

    def test_percentual_dia_integral(self):
        ap = self._make_parcial(self.aloc1, 8)
        ap.save()
        self.assertEqual(ap.percentual_dia, 100.0)

    def test_turno_descricao_meio_periodo(self):
        ap = self._make_parcial(self.aloc1, 4)
        ap.save()
        self.assertEqual(ap.turno_descricao, "Meio período")

    def test_turno_descricao_integral(self):
        ap = self._make_parcial(self.aloc1, 8)
        ap.save()
        self.assertEqual(ap.turno_descricao, "Dedicação integral")

    def test_turno_descricao_parcial(self):
        ap = self._make_parcial(self.aloc1, 6)
        ap.save()
        self.assertEqual(ap.turno_descricao, "Dedicação parcial")

    def test_turno_descricao_suporte(self):
        ap = self._make_parcial(self.aloc1, 2)
        ap.save()
        self.assertEqual(ap.turno_descricao, "Suporte pontual")

    def test_horas_usadas_classmethod(self):
        from apps.projetos.models import AlocacaoParcial
        AlocacaoParcial.objects.create(
            id_colaborador=self.colab, id_alocacao=self.aloc1,
            horas_dia=Decimal("3.0"), dt_inicio=date.today(),
        )
        AlocacaoParcial.objects.create(
            id_colaborador=self.colab, id_alocacao=self.aloc2,
            horas_dia=Decimal("2.0"), dt_inicio=date.today(),
        )
        usadas = AlocacaoParcial.horas_usadas(self.colab)
        self.assertEqual(usadas, 5.0)

    def test_parcial_encerrada_nao_conta_horas(self):
        """Alocação com dt_fim não conta para o total de horas ativas."""
        from apps.projetos.models import AlocacaoParcial
        AlocacaoParcial.objects.create(
            id_colaborador=self.colab, id_alocacao=self.aloc1,
            horas_dia=Decimal("7.0"), dt_inicio=date.today() - timedelta(days=30),
            dt_fim=date.today() - timedelta(days=1),  # encerrada
        )
        # Nova alocação ativa de 8h deve ser válida pois a anterior está encerrada
        ap = self._make_parcial(self.aloc2, 8)
        ap.save()
        self.assertEqual(float(ap.horas_dia), 8.0)

    def test_str_alocacao_parcial(self):
        ap = self._make_parcial(self.aloc1, 4)
        ap.save()
        self.assertIn("4", str(ap))
        self.assertIn("Test User", str(ap))


# ── Notebook / NotebookHistorico ──────────────────────────────────────────────

class NotebookModelTests(TestCase):
    def setUp(self):
        self.colab = make_colaborador()

    def _make_notebook(self, serie="NB-001", eh_ntt=True):
        from apps.notebooks.models import Notebook
        # Desconectar signal para teste limpo
        from django.db.models.signals import post_save
        from apps.notebooks.signals import historico_inicial
        post_save.disconnect(historico_inicial, sender=Notebook)
        nb = Notebook.objects.create(
            numero_serie=serie, eh_ntt=eh_ntt,
            modelo="Test Model", marca="Dell", ativo=True,
        )
        post_save.connect(historico_inicial, sender=Notebook)
        return nb

    def test_notebook_criado(self):
        nb = self._make_notebook()
        self.assertEqual(nb.numero_serie, "NB-001")

    def test_origem_ntt(self):
        nb = self._make_notebook(eh_ntt=True)
        self.assertEqual(nb.origem, "NTT Data")

    def test_origem_cliente(self):
        from apps.notebooks.models import Notebook
        from django.db.models.signals import post_save
        from apps.notebooks.signals import historico_inicial
        post_save.disconnect(historico_inicial, sender=Notebook)
        nb = Notebook.objects.create(
            numero_serie="NB-CLI", eh_ntt=False, eh_cliente=True,
            modelo="MacBook", marca="Apple", ativo=True,
        )
        post_save.connect(historico_inicial, sender=Notebook)
        self.assertEqual(nb.origem, "Cliente")

    def test_str_notebook(self):
        nb = self._make_notebook()
        self.assertIn("NB-001", str(nb))


class NotebookHistoricoTests(TestCase):
    def setUp(self):
        self.colab = make_colaborador()
        from apps.notebooks.models import Notebook
        from django.db.models.signals import post_save
        from apps.notebooks.signals import historico_inicial
        post_save.disconnect(historico_inicial, sender=Notebook)
        self.nb = Notebook.objects.create(
            numero_serie="NB-H01", eh_ntt=True,
            modelo="Latitude", marca="Dell", ativo=True,
        )
        post_save.connect(historico_inicial, sender=Notebook)

    def test_criar_historico(self):
        from apps.notebooks.models import NotebookHistorico
        h = NotebookHistorico.objects.create(
            notebook=self.nb,
            responsavel=self.colab,
            dt_inicio=date.today() - timedelta(days=60),
            dt_fim=date.today() - timedelta(days=30),
        )
        self.assertFalse(h.ativo)

    def test_historico_ativo(self):
        from apps.notebooks.models import NotebookHistorico
        h = NotebookHistorico.objects.create(
            notebook=self.nb,
            responsavel=self.colab,
            dt_inicio=date.today() - timedelta(days=30),
        )
        self.assertTrue(h.ativo)

    def test_duracao_meses(self):
        from apps.notebooks.models import NotebookHistorico
        h = NotebookHistorico.objects.create(
            notebook=self.nb,
            responsavel=self.colab,
            dt_inicio=date.today() - timedelta(days=90),
            dt_fim=date.today(),
        )
        self.assertIn("m", h.duracao)  # "X meses" ou similar

    def test_duracao_dias(self):
        from apps.notebooks.models import NotebookHistorico
        h = NotebookHistorico.objects.create(
            notebook=self.nb,
            dt_inicio=date.today() - timedelta(days=5),
            dt_fim=date.today(),
        )
        self.assertIn("dia", h.duracao)

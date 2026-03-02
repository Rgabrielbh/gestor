"""Testes de views frontend (session-based) — ≥98% acurácia."""
from django.test import TestCase, Client
from django.urls import reverse
from datetime import date, timedelta
from apps.colaboradores.models import Colaborador, RoleChoices


def make_user(username="u1", email="u1@nttdata.com", role=RoleChoices.OPERADOR, **kwargs):
    u = Colaborador(username=username, email=email, nome="User One", role=role, **kwargs)
    u.set_password("Senha@123")
    u.save()
    return u


def make_cliente(nome="Cliente A", cnpj="00.000.000/0001-00"):
    from apps.clientes.models import Cliente
    return Cliente.objects.create(nome=nome, cnpj=cnpj)


def make_projeto(cliente, nome="Projeto Alpha"):
    from apps.projetos.models import Projeto
    return Projeto.objects.create(
        nome_proj_ntt=nome, id_cliente=cliente,
        qte_pessoas=4, qte_pessoas_atual=2,
    )


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()
        self.url = reverse("login")

    def test_get_login_page(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "NTT")

    def test_post_login_username(self):
        resp = self.client.post(self.url,
            {"username": "u1", "password": "Senha@123"}, follow=True)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_post_login_email(self):
        resp = self.client.post(self.url,
            {"username": "u1@nttdata.com", "password": "Senha@123"}, follow=True)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_login_errado_nao_autentica(self):
        resp = self.client.post(self.url, {"username": "u1", "password": "errada"})
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_redirect_se_logado(self):
        self.client.force_login(self.user)
        resp = self.client.get(self.url)
        self.assertRedirects(resp, reverse("dashboard:index"))


class ColaboradorListViewTests(TestCase):
    def test_requer_login(self):
        resp = self.client.get(reverse("colaboradores-list"))
        self.assertRedirects(resp, "/auth/login/?next=/colaboradores/")

    def test_operador_ve_apenas_si(self):
        u1 = make_user()
        make_user(username="u2", email="u2@nttdata.com")
        self.client.force_login(u1)
        resp = self.client.get(reverse("colaboradores-list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["colaboradores"].count(), 1)

    def test_gestor_ve_todos(self):
        gestor = make_user(username="g1", email="g1@nttdata.com", role=RoleChoices.GESTOR)
        make_user(username="u2", email="u2@nttdata.com")
        make_user(username="u3", email="u3@nttdata.com")
        self.client.force_login(gestor)
        resp = self.client.get(reverse("colaboradores-list"))
        self.assertGreaterEqual(resp.context["colaboradores"].count(), 3)


class RegisterViewTests(TestCase):
    def test_operador_nao_acessa_register(self):
        u = make_user()
        self.client.force_login(u)
        resp = self.client.get(reverse("register"))
        self.assertNotEqual(resp.status_code, 200)

    def test_gestor_acessa_register(self):
        g = make_user(username="g1", email="g1@nttdata.com", role=RoleChoices.GESTOR)
        self.client.force_login(g)
        resp = self.client.get(reverse("register"))
        self.assertEqual(resp.status_code, 200)


class DashboardViewTests(TestCase):
    def test_dashboard_requer_login(self):
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 302)

    def test_dashboard_ok_logado(self):
        u = make_user()
        self.client.force_login(u)
        resp = self.client.get(reverse("dashboard:index"))
        self.assertEqual(resp.status_code, 200)


class TimelineViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def test_timeline_index(self):
        resp = self.client.get(reverse("timeline:index"))
        self.assertEqual(resp.status_code, 200)

    def test_timeline_colaborador_sem_q(self):
        resp = self.client.get(reverse("timeline:colaborador"))
        self.assertEqual(resp.status_code, 200)

    def test_timeline_colaborador_busca(self):
        resp = self.client.get(reverse("timeline:colaborador") + "?q=User&modo=colaborador")
        self.assertEqual(resp.status_code, 200)

    def test_timeline_colaborador_busca_sem_resultado(self):
        resp = self.client.get(reverse("timeline:colaborador") + "?q=XYZ999&modo=colaborador")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context["resultado"])
        self.assertEqual(len(resp.context["sugestoes"]), 0)

    def test_timeline_colaborador_match_unico(self):
        resp = self.client.get(reverse("timeline:colaborador") + "?q=User One&modo=colaborador")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["resultado"])

    def test_timeline_projeto_busca(self):
        cliente = make_cliente()
        make_projeto(cliente)
        resp = self.client.get(reverse("timeline:colaborador") + "?q=Alpha&modo=projeto")
        self.assertEqual(resp.status_code, 200)

    def test_timeline_notebook_sem_q(self):
        resp = self.client.get(reverse("timeline:notebook"))
        self.assertEqual(resp.status_code, 200)

    def test_timeline_notebook_busca(self):
        resp = self.client.get(reverse("timeline:notebook") + "?q=Dell&modo=notebook")
        self.assertEqual(resp.status_code, 200)

    def test_timeline_notebook_por_periodo(self):
        resp = self.client.get(
            reverse("timeline:notebook") + "?modo=periodo&dt_inicio=2024-01-01&dt_fim=2024-12-31"
        )
        self.assertEqual(resp.status_code, 200)


class AlocacaoParcialViewTests(TestCase):
    """Testa que a timeline exibe corretamente a divisão de horas."""

    def setUp(self):
        from decimal import Decimal
        from apps.projetos.models import ColaboradorProjeto, AlocacaoParcial

        self.user = make_user()
        self.client.force_login(self.user)

        self.cliente1 = make_cliente(nome="Itaú", cnpj="11.111.111/0001-11")
        self.cliente2 = make_cliente(nome="Magalu", cnpj="22.222.222/0001-22")
        self.proj1 = make_projeto(self.cliente1, nome="Itaú Open Banking")
        self.proj2 = make_projeto(self.cliente2, nome="Magalu Digital")

        self.aloc1 = ColaboradorProjeto.objects.create(
            id_proj=self.proj1, id_colaborador=self.user,
            id_cliente=self.cliente1,
            dt_inicio=date.today() - timedelta(days=60),
            funcao="Dev Backend",
        )
        self.aloc2 = ColaboradorProjeto.objects.create(
            id_proj=self.proj2, id_colaborador=self.user,
            id_cliente=self.cliente2,
            dt_inicio=date.today() - timedelta(days=30),
            funcao="Dev Frontend",
        )
        AlocacaoParcial.objects.create(
            id_colaborador=self.user, id_alocacao=self.aloc1,
            horas_dia=Decimal("3.0"), dt_inicio=date.today() - timedelta(days=30),
        )
        AlocacaoParcial.objects.create(
            id_colaborador=self.user, id_alocacao=self.aloc2,
            horas_dia=Decimal("5.0"), dt_inicio=date.today() - timedelta(days=30),
        )

    def test_timeline_exibe_alocacoes_parciais(self):
        resp = self.client.get(
            reverse("timeline:colaborador") + f"?q=User One&modo=colaborador"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.context["resultado"])
        self.assertEqual(len(resp.context["alocacoes_parciais"]), 2)

    def test_horas_total_correto(self):
        resp = self.client.get(
            reverse("timeline:colaborador") + f"?q=User One&modo=colaborador"
        )
        self.assertEqual(resp.context["horas_total"], 8.0)

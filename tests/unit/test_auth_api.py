"""Testes de integração — API de Autenticação."""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.colaboradores.models import Colaborador, RoleChoices


def make_user(username="user1", email="user1@nttdata.com", role=RoleChoices.OPERADOR, **kwargs):
    u = Colaborador(username=username, email=email, nome="User One", role=role, **kwargs)
    u.set_password("Senha@Teste123")
    u.save()
    return u


class LoginAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.url = "/api/v1/auth/token/"

    def test_login_ok_username(self):
        resp = self.client.post(self.url, {"username": "user1", "password": "Senha@Teste123"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.assertEqual(resp.data["user"]["username"], "user1")

    def test_login_ok_email(self):
        resp = self.client.post(self.url, {"username": "user1@nttdata.com", "password": "Senha@Teste123"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        resp = self.client.post(self.url, {"username": "user1", "password": "errada"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        resp = self.client.post(self.url, {"username": "nobody", "password": "Senha@123"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class MeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.url = "/api/v1/auth/me/"

    def test_me_sem_auth(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_com_auth(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "user1")

    def test_me_nao_expoe_role_update(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.url, {"role": "diretor"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, RoleChoices.OPERADOR)  # role é read_only


class RegisterAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.operador = make_user()
        self.gestor = make_user(username="g1", email="g1@nttdata.com", role=RoleChoices.GESTOR)
        self.url = "/api/v1/auth/register/"

    def test_operador_nao_pode_criar(self):
        self.client.force_authenticate(user=self.operador)
        resp = self.client.post(self.url, {
            "username": "novo", "email": "novo@ntt.com",
            "nome": "Novo", "password": "Novo@Pass123", "password_confirm": "Novo@Pass123"
        })
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_gestor_pode_criar(self):
        self.client.force_authenticate(user=self.gestor)
        resp = self.client.post(self.url, {
            "username": "colabo", "email": "colabo@ntt.com",
            "nome": "Colaborador Teste", "password": "Novo@Pass123", "password_confirm": "Novo@Pass123"
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Colaborador.objects.filter(username="colabo").exists())

    def test_senha_fraca_rejeitada(self):
        self.client.force_authenticate(user=self.gestor)
        resp = self.client.post(self.url, {
            "username": "fraco", "email": "fraco@ntt.com",
            "nome": "Fraco", "password": "123", "password_confirm": "123"
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_senha_divergente_rejeitada(self):
        self.client.force_authenticate(user=self.gestor)
        resp = self.client.post(self.url, {
            "username": "div", "email": "div@ntt.com",
            "nome": "Div", "password": "Div@Pass123", "password_confirm": "Diferente@123"
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_duplicado_rejeitado(self):
        self.client.force_authenticate(user=self.gestor)
        resp = self.client.post(self.url, {
            "username": "dup", "email": "user1@nttdata.com",  # email já existe
            "nome": "Dup", "password": "Dup@Pass123", "password_confirm": "Dup@Pass123"
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()

    def test_logout_blacklists_refresh(self):
        """Requer rest_framework_simplejwt.token_blacklist em INSTALLED_APPS."""
        from django.apps import apps
        if not apps.is_installed("rest_framework_simplejwt.token_blacklist"):
            self.skipTest("token_blacklist não instalado neste ambiente de teste.")
        login = self.client.post("/api/v1/auth/token/", {
            "username": "user1", "password": "Senha@Teste123"
        })
        refresh = login.data["refresh"]
        access = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp = self.client.post("/api/v1/auth/logout/", {"refresh": refresh})
        self.assertEqual(resp.status_code, status.HTTP_205_RESET_CONTENT)

    def test_logout_sem_auth_rejeitado(self):
        resp = self.client.post("/api/v1/auth/logout/", {"refresh": "token_invalido"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

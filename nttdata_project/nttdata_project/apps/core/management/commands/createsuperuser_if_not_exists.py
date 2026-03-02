from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

class Command(BaseCommand):
    help = "Cria superusuário padrão se não existir."

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = config("DJANGO_SUPERUSER_USERNAME", default="admin")
        email = config("DJANGO_SUPERUSER_EMAIL", default="admin@nttdata.com")
        password = config("DJANGO_SUPERUSER_PASSWORD", default="Admin@123456")
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, email=email, password=password,
                nome="Administrador NTT Data", role="diretor",
            )
            self.stdout.write(self.style.SUCCESS(f"Superusuario '{username}' criado."))
        else:
            self.stdout.write(f"Superusuario '{username}' ja existe.")

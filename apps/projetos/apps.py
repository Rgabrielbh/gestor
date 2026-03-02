from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ProjetosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projetos"
    verbose_name = _("Projetos")

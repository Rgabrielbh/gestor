from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class RelatoriosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.relatorios"
    verbose_name = _("Relatorios")

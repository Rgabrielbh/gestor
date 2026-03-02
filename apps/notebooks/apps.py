from django.apps import AppConfig


class NotebooksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notebooks"
    verbose_name = "Notebooks"

    def ready(self):
        import apps.notebooks.signals  # noqa

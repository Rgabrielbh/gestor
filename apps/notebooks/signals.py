from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(pre_save, sender="notebooks.Notebook")
def registrar_historico_notebook(sender, instance, **kwargs):
    """Quando o responsável ou localização muda, fecha o registro atual e abre um novo."""
    if not instance.pk:
        return  # criação nova — histórico será criado no post_save

    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    mudou_responsavel = anterior.responsavel_id != instance.responsavel_id
    mudou_localizacao = anterior.localizacao != instance.localizacao

    if mudou_responsavel or mudou_localizacao:
        from apps.notebooks.models import NotebookHistorico
        hoje = timezone.now().date()
        # Fechar registro atual
        NotebookHistorico.objects.filter(
            notebook=anterior, dt_fim__isnull=True
        ).update(dt_fim=hoje)

        # Abrir novo registro
        NotebookHistorico.objects.create(
            notebook=instance,
            responsavel=instance.responsavel,
            localizacao=instance.localizacao or "",
            dt_inicio=hoje,
        )


@receiver(pre_save, sender="notebooks.Notebook")
def criar_historico_inicial(sender, instance, **kwargs):
    """Cria o primeiro registro de histórico ao criar um notebook."""
    pass  # tratado no post_save abaixo


from django.db.models.signals import post_save

@receiver(post_save, sender="notebooks.Notebook")
def historico_inicial(sender, instance, created, **kwargs):
    if created:
        from apps.notebooks.models import NotebookHistorico
        NotebookHistorico.objects.create(
            notebook=instance,
            responsavel=instance.responsavel,
            localizacao=instance.localizacao or "",
            dt_inicio=timezone.now().date(),
        )

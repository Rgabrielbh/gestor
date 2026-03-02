from django.contrib import admin
from .models import Contrato

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ["codigo","cliente","dt_inicio","dt_fim","renova","fte"]
    list_filter = ["renova","cliente"]
    search_fields = ["codigo","resp_cliente"]

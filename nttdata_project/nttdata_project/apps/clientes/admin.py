from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nome","cnpj","resp_nttdata"]
    search_fields = ["nome","cnpj"]

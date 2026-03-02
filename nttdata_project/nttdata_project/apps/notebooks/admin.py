from django.contrib import admin
from .models import Notebook

@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ["numero_serie","marca","modelo","responsavel","origem","ativo","localizacao"]
    list_filter = ["eh_ntt","eh_cliente","ativo"]
    search_fields = ["numero_serie","responsavel__nome","modelo","marca"]

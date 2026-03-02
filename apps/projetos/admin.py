from django.contrib import admin
from .models import Projeto, GestorProjeto, ColaboradorProjeto

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ["nome_proj_ntt","id_cliente","gestor","qte_pessoas","qte_pessoas_atual","ativo","contrato_pend"]
    list_filter = ["ativo","contrato_pend","id_cliente"]
    search_fields = ["nome_proj_ntt","ov"]

@admin.register(GestorProjeto)
class GestorProjetoAdmin(admin.ModelAdmin):
    list_display = ["nome_proj","id_gp","id_cliente"]

@admin.register(ColaboradorProjeto)
class ColaboradorProjetoAdmin(admin.ModelAdmin):
    list_display = ["nome_colaborador","nome_proj","id_cliente","funcao","squad","dt_inicio","dt_fim"]
    list_filter = ["id_cliente","dt_fim"]
    search_fields = ["nome_colaborador","nome_proj","squad"]

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Colaborador

@admin.register(Colaborador)
class ColaboradorAdmin(UserAdmin):
    list_display = ["username","nome","email","role","status","cargo","cidade","is_active"]
    list_filter = ["role","status","is_active","is_staff","cidade","estado"]
    search_fields = ["username","nome","email","matricula","cargo"]
    ordering = ["nome"]
    fieldsets = (
        (None, {"fields": ("username","password")}),
        (_("Informações pessoais"), {"fields": ("nome","email","telefone","avatar")}),
        (_("Dados profissionais"), {"fields": ("matricula","pos","req","cargo","funcao","cidade","estado","local_escritorio","dt_admissao","dt_demissao","salario")}),
        (_("Hierarquia"), {"fields": ("gestor_direto","cod_gestor_sup","cod_gestor","nome_gestor")}),
        (_("Acesso"), {"fields": ("role","status","is_active","is_staff","is_superuser","groups","user_permissions")}),
        (_("Datas"), {"fields": ("last_login","date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("username","nome","email","role","password1","password2")}),)
    readonly_fields = ["last_login","date_joined"]

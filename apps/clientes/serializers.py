from rest_framework import serializers
from .models import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    total_projetos = serializers.SerializerMethodField()
    total_colaboradores = serializers.IntegerField(source="total_colaboradores", read_only=True)
    class Meta:
        model = Cliente
        fields = ["id","cnpj","nome","resp_nttdata","total_projetos","total_colaboradores","criado_em","atualizado_em"]
        read_only_fields = ["criado_em","atualizado_em"]

    def get_total_projetos(self, obj):
        return obj.projetos.filter(ativo=True).count()

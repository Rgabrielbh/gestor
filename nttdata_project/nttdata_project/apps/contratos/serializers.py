from rest_framework import serializers
from .models import Contrato
from apps.clientes.serializers import ClienteSerializer

class ContratoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="cliente.nome", read_only=True)
    ativo = serializers.BooleanField(read_only=True)
    dias_para_vencimento = serializers.IntegerField(read_only=True)
    class Meta:
        model = Contrato
        fields = ["id","codigo","descricao","cliente","cliente_nome","fte","dt_inicio","dt_fim",
                  "renova","ov_anterior","resp_cliente","ativo","dias_para_vencimento","criado_em","atualizado_em"]
        read_only_fields = ["criado_em","atualizado_em"]

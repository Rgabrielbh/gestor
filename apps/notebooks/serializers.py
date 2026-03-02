from rest_framework import serializers
from .models import Notebook

class NotebookSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source="responsavel.nome", read_only=True)
    origem = serializers.CharField(read_only=True)
    class Meta:
        model = Notebook
        fields = ["id","numero_serie","eh_ntt","patrimonio_ntt","eh_cliente","patrimonio_cliente",
                  "localizacao","responsavel","responsavel_nome","modelo","marca","ativo","observacoes",
                  "origem","criado_em","atualizado_em"]
        read_only_fields = ["criado_em","atualizado_em"]

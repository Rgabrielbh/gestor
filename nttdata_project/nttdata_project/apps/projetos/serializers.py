from rest_framework import serializers
from .models import Projeto, GestorProjeto, ColaboradorProjeto

class ProjetoListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source="id_cliente.nome", read_only=True)
    gestor_nome = serializers.CharField(source="gestor.nome", read_only=True)
    percentual_alocacao = serializers.FloatField(read_only=True)
    class Meta:
        model = Projeto
        fields = ["id","nome_proj_ntt","descricao","id_cliente","cliente_nome","contrato",
                  "qte_pessoas","qte_pessoas_atual","percentual_alocacao","contrato_pend",
                  "ov","gestor","gestor_nome","ativo","criado_em","atualizado_em"]

class GestorProjetoSerializer(serializers.ModelSerializer):
    gp_nome = serializers.CharField(source="id_gp.nome", read_only=True)
    tot_colaboradores = serializers.IntegerField(read_only=True)
    class Meta:
        model = GestorProjeto
        fields = ["id","id_projeto","nome_proj","id_cliente","id_gp","gp_nome",
                  "id_colaborador","nome_colaborador","tot_colaboradores","criado_em"]

class ColaboradorProjetoSerializer(serializers.ModelSerializer):
    colaborador_nome = serializers.CharField(source="id_colaborador.nome", read_only=True)
    projeto_nome = serializers.CharField(source="id_proj.nome_proj_ntt", read_only=True)
    cliente_nome = serializers.CharField(source="id_cliente.nome", read_only=True)
    ativo = serializers.BooleanField(read_only=True)
    class Meta:
        model = ColaboradorProjeto
        fields = ["id","id_proj","projeto_nome","id_cliente","cliente_nome","id_colaborador","colaborador_nome",
                  "nome_proj","ov_projeto","centro_custo","custo_projeto","funcao","dt_inicio","dt_fim",
                  "squad","contato_projeto","resp_cliente","p01","p02","gestor","ativo","criado_em","atualizado_em"]
        read_only_fields = ["criado_em","atualizado_em"]

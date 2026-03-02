from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Projeto, GestorProjeto, ColaboradorProjeto
from .serializers import ProjetoListSerializer, GestorProjetoSerializer, ColaboradorProjetoSerializer

class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.select_related("id_cliente","gestor","contrato").order_by("nome_proj_ntt")
    serializer_class = ProjetoListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nome_proj_ntt","ov","id_cliente__nome"]
    filterset_fields = ["id_cliente","ativo","contrato_pend","gestor"]

class GestorProjetoViewSet(viewsets.ModelViewSet):
    queryset = GestorProjeto.objects.select_related("id_projeto","id_cliente","id_gp").all()
    serializer_class = GestorProjetoSerializer
    permission_classes = [permissions.IsAuthenticated]

class ColaboradorProjetoViewSet(viewsets.ModelViewSet):
    queryset = ColaboradorProjeto.objects.select_related("id_proj","id_cliente","id_colaborador").order_by("-dt_inicio")
    serializer_class = ColaboradorProjetoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nome_colaborador","nome_proj","squad","funcao"]
    filterset_fields = ["id_proj","id_cliente","id_colaborador","dt_fim"]

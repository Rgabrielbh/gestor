from django.urls import path
from .views_api import (
    RelatorioColaboradoresCSV, RelatorioColaboradoresPDF,
    RelatorioProjetosCSV, RelatorioProjetosPDF,
    RelatorioAlocacoesCSV, RelatorioAlocacoesPDF,
    RelatorioNotebooksCSV, RelatorioNotebooksPDF,
)

urlpatterns = [
    path("colaboradores/csv/", RelatorioColaboradoresCSV.as_view(), name="rel-colaboradores-csv"),
    path("colaboradores/pdf/", RelatorioColaboradoresPDF.as_view(), name="rel-colaboradores-pdf"),
    path("projetos/csv/",      RelatorioProjetosCSV.as_view(),      name="rel-projetos-csv"),
    path("projetos/pdf/",      RelatorioProjetosPDF.as_view(),      name="rel-projetos-pdf"),
    path("alocacoes/csv/",     RelatorioAlocacoesCSV.as_view(),     name="rel-alocacoes-csv"),
    path("alocacoes/pdf/",     RelatorioAlocacoesPDF.as_view(),     name="rel-alocacoes-pdf"),
    path("notebooks/csv/",     RelatorioNotebooksCSV.as_view(),     name="rel-notebooks-csv"),
    path("notebooks/pdf/",     RelatorioNotebooksPDF.as_view(),     name="rel-notebooks-pdf"),
]

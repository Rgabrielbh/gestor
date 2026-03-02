import django_filters
from .models import Colaborador, RoleChoices, StatusColaborador

class ColaboradorFilter(django_filters.FilterSet):
    nome = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    cargo = django_filters.CharFilter(lookup_expr="icontains")
    cidade = django_filters.CharFilter(lookup_expr="icontains")
    estado = django_filters.CharFilter(lookup_expr="iexact")
    role = django_filters.ChoiceFilter(choices=RoleChoices.choices)
    status = django_filters.ChoiceFilter(choices=StatusColaborador.choices)
    dt_admissao_after = django_filters.DateFilter(field_name="dt_admissao", lookup_expr="gte")
    dt_admissao_before = django_filters.DateFilter(field_name="dt_admissao", lookup_expr="lte")
    class Meta:
        model = Colaborador
        fields = ["nome","email","cargo","cidade","estado","role","status"]

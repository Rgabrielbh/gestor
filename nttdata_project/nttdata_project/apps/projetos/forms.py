from django import forms
from .models import Projeto, GestorProjeto, ColaboradorProjeto
from apps.colaboradores.models import Colaborador

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ["nome_proj_ntt","descricao","id_cliente","contrato","qte_pessoas",
                  "qte_pessoas_atual","contrato_pend","ov","gestor","ativo"]
        widgets = {
            "nome_proj_ntt": forms.TextInput(attrs={"class":"form-control"}),
            "descricao": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "id_cliente": forms.Select(attrs={"class":"form-select"}),
            "contrato": forms.Select(attrs={"class":"form-select"}),
            "qte_pessoas": forms.NumberInput(attrs={"class":"form-control"}),
            "qte_pessoas_atual": forms.NumberInput(attrs={"class":"form-control"}),
            "contrato_pend": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "ov": forms.TextInput(attrs={"class":"form-control"}),
            "gestor": forms.Select(attrs={"class":"form-select"}),
            "ativo": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

class ColaboradorProjetoForm(forms.ModelForm):
    class Meta:
        model = ColaboradorProjeto
        fields = ["id_proj","id_colaborador","id_cliente","funcao","squad","dt_inicio","dt_fim",
                  "centro_custo","custo_projeto","ov_projeto","resp_cliente","contato_projeto","p01","p02","gestor"]
        widgets = {
            "id_proj": forms.Select(attrs={"class":"form-select"}),
            "id_colaborador": forms.Select(attrs={"class":"form-select"}),
            "id_cliente": forms.Select(attrs={"class":"form-select"}),
            "funcao": forms.TextInput(attrs={"class":"form-control"}),
            "squad": forms.TextInput(attrs={"class":"form-control"}),
            "dt_inicio": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "dt_fim": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "centro_custo": forms.TextInput(attrs={"class":"form-control"}),
            "custo_projeto": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "ov_projeto": forms.TextInput(attrs={"class":"form-control"}),
            "resp_cliente": forms.TextInput(attrs={"class":"form-control"}),
            "contato_projeto": forms.TextInput(attrs={"class":"form-control"}),
            "p01": forms.Select(attrs={"class":"form-select"}),
            "p02": forms.Select(attrs={"class":"form-select"}),
            "gestor": forms.Select(attrs={"class":"form-select"}),
        }

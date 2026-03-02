from django import forms
from .models import Contrato

class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ["codigo","descricao","cliente","fte","dt_inicio","dt_fim","renova","ov_anterior","resp_cliente"]
        widgets = {
            "codigo": forms.TextInput(attrs={"class":"form-control"}),
            "descricao": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "cliente": forms.Select(attrs={"class":"form-select"}),
            "fte": forms.NumberInput(attrs={"class":"form-control","step":"0.1"}),
            "dt_inicio": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "dt_fim": forms.DateInput(attrs={"class":"form-control","type":"date"}),
            "renova": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "ov_anterior": forms.TextInput(attrs={"class":"form-control"}),
            "resp_cliente": forms.TextInput(attrs={"class":"form-control"}),
        }

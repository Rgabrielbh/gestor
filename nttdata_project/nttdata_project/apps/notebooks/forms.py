from django import forms
from .models import Notebook

class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        fields = ["numero_serie","eh_ntt","patrimonio_ntt","eh_cliente","patrimonio_cliente",
                  "localizacao","responsavel","modelo","marca","ativo","observacoes"]
        widgets = {
            "numero_serie": forms.TextInput(attrs={"class":"form-control"}),
            "patrimonio_ntt": forms.TextInput(attrs={"class":"form-control"}),
            "patrimonio_cliente": forms.TextInput(attrs={"class":"form-control"}),
            "localizacao": forms.TextInput(attrs={"class":"form-control"}),
            "responsavel": forms.Select(attrs={"class":"form-select"}),
            "modelo": forms.TextInput(attrs={"class":"form-control"}),
            "marca": forms.TextInput(attrs={"class":"form-control"}),
            "observacoes": forms.Textarea(attrs={"class":"form-control","rows":3}),
            "eh_ntt": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "eh_cliente": forms.CheckboxInput(attrs={"class":"form-check-input"}),
            "ativo": forms.CheckboxInput(attrs={"class":"form-check-input"}),
        }

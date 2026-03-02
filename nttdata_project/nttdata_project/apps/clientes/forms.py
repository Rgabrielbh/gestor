from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["cnpj","nome","resp_nttdata"]
        widgets = {
            "cnpj": forms.TextInput(attrs={"class":"form-control","placeholder":"XX.XXX.XXX/XXXX-XX"}),
            "nome": forms.TextInput(attrs={"class":"form-control"}),
            "resp_nttdata": forms.TextInput(attrs={"class":"form-control"}),
        }

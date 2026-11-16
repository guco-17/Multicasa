from django import forms

from .models import MensajeContacto


class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'correo', 'telefono', 'mensaje']
        widgets = {
            'mensaje': forms.Textarea(attrs={'rows': 5}),
        }

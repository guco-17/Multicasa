from django import forms

from apps.casas.models import Casa

from .models import MensajeContacto


class ContactoForm(forms.ModelForm):
    casa = forms.ModelChoiceField(
        queryset=Casa.objects.filter(activo=True, estatus='en_venta').order_by('titulo'),
        required=False,
        widget=forms.HiddenInput(),
    )
    casa_busqueda = forms.CharField(
        label='Casa que te interesa (opcional)',
        required=False,
        max_length=500,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'search',
                'placeholder': 'Escribe el nombre o la dirección',
                'autocomplete': 'off',
                'role': 'combobox',
                'aria-autocomplete': 'list',
                'aria-expanded': 'false',
                'aria-controls': 'casa-search-results',
            }
        ),
    )

    class Meta:
        model = MensajeContacto
        fields = ['casa', 'nombre', 'correo', 'telefono', 'mensaje']
        labels = {
            'nombre': 'Nombre',
            'correo': 'Correo electrónico',
            'telefono': 'Teléfono (opcional)',
            'mensaje': '¿En qué podemos ayudarte?',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        casa = cleaned_data.get('casa')
        busqueda = cleaned_data.get('casa_busqueda', '').strip()

        if casa:
            etiqueta = f'{casa.titulo} — {casa.direccion}, {casa.ciudad}'
            if busqueda != etiqueta:
                self.add_error(
                    'casa_busqueda',
                    'Selecciona una propiedad de los resultados de búsqueda.',
                )
        elif busqueda:
            self.add_error(
                'casa_busqueda',
                'Selecciona una propiedad de los resultados de búsqueda.',
            )

        return cleaned_data


class MensajeContactoGestionForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = '__all__'

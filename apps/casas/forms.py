from decimal import Decimal

from django import forms

from .models import Casa


class CasaBusquedaForm(forms.Form):
    ciudad = forms.CharField(
        label='Ciudad o zona',
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Ej. Saltillo',
            }
        ),
    )
    estatus = forms.ChoiceField(
        label='Tipo de operación',
        choices=[('', 'Cualquiera'), *Casa.ESTATUS_CHOICES],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    precio_min = forms.DecimalField(
        label='Precio desde',
        required=False,
        min_value=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Mínimo',
                'step': '0.01',
            }
        ),
    )
    precio_max = forms.DecimalField(
        label='Precio hasta',
        required=False,
        min_value=Decimal('0'),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control form-control-sm',
                'placeholder': 'Máximo',
                'step': '0.01',
            }
        ),
    )
    recamaras = forms.IntegerField(
        label='Recámaras',
        required=False,
        min_value=0,
        widget=forms.Select(
            choices=[('', 'Cualquiera')] + [(n, str(n)) for n in range(1, 7)],
            attrs={'class': 'form-select form-select-sm'},
        ),
    )
    banos = forms.DecimalField(
        label='Baños',
        required=False,
        min_value=Decimal('0'),
        max_digits=3,
        decimal_places=1,
        widget=forms.Select(
            choices=[('', 'Cualquiera')] + [(str(n / 2), f'{n / 2:g}') for n in range(1, 11)],
            attrs={'class': 'form-select form-select-sm'},
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        precio_min = cleaned_data.get('precio_min')
        precio_max = cleaned_data.get('precio_max')

        if precio_min is not None and precio_max is not None and precio_min > precio_max:
            self.add_error('precio_max', 'El precio máximo debe ser mayor o igual al mínimo.')

        return cleaned_data

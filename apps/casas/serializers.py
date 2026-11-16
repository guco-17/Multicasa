from rest_framework import serializers

from .models import Casa


class CasaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Casa
        fields = [
            'id',
            'titulo',
            'descripcion',
            'precio',
            'direccion',
            'ciudad',
            'zona',
            'latitud',
            'longitud',
            'recamaras',
            'banos',
            'metros_construccion',
            'metros_terreno',
            'estatus',
            'activo',
            'fecha_registro',
        ]
        read_only_fields = ['id', 'fecha_registro']

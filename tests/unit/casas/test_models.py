from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.casas.models import Casa, Imagen


class CasaModelTests(TestCase):
    def casa_data(self, **overrides):
        data = {
            'titulo': 'Casa de prueba',
            'descripcion': 'Descripción de prueba',
            'precio': Decimal('1850000.00'),
            'direccion': 'Calle de prueba 123',
            'ciudad': 'Saltillo',
            'zona': 'Centro',
            'latitud': Decimal('25.4383000'),
            'longitud': Decimal('-100.9737000'),
            'recamaras': 3,
            'banos': Decimal('2.0'),
            'metros_construccion': Decimal('180.00'),
            'metros_terreno': Decimal('220.00'),
        }
        data.update(overrides)
        return data

    def test_new_house_defaults_to_active_for_sale(self):
        casa = Casa.objects.create(**self.casa_data())

        self.assertEqual(casa.estatus, 'en_venta')
        self.assertTrue(casa.activo)

    def test_validation_rejects_invalid_price_and_coordinates(self):
        casa = Casa(**self.casa_data(precio=Decimal('0'), latitud=Decimal('91')))

        with self.assertRaises(ValidationError):
            casa.full_clean()

    def test_images_are_related_to_their_house(self):
        casa = Casa.objects.create(**self.casa_data())
        imagen = Imagen.objects.create(
            casa=casa,
            ruta_imagen='casas/prueba.jpg',
            es_principal=True,
        )

        self.assertEqual(casa.imagenes.get(), imagen)

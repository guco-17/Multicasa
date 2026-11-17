from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.casas.models import Casa, Imagen


class CasaSearchViewTests(TestCase):
    def test_home_shows_active_houses_for_sale_without_search_filters(self):
        Casa.objects.create(
            titulo='Casa disponible',
            descripcion='Casa de prueba',
            precio=Decimal('1850000.00'),
            direccion='Calle de prueba 123',
            ciudad='Saltillo',
            zona='Centro',
            latitud=Decimal('25.4383000'),
            longitud=Decimal('-100.9737000'),
            recamaras=3,
            banos=Decimal('2.0'),
            metros_construccion=Decimal('180.00'),
            metros_terreno=Decimal('220.00'),
        )
        Casa.objects.create(
            titulo='Casa vendida',
            descripcion='Casa vendida de prueba',
            precio=Decimal('1850000.00'),
            direccion='Calle de prueba 456',
            ciudad='Saltillo',
            zona='Centro',
            latitud=Decimal('25.4383000'),
            longitud=Decimal('-100.9737000'),
            recamaras=3,
            banos=Decimal('2.0'),
            metros_construccion=Decimal('180.00'),
            metros_terreno=Decimal('220.00'),
            estatus='vendida',
        )
        Casa.objects.create(
            titulo='Casa desactivada',
            descripcion='Casa desactivada de prueba',
            precio=Decimal('1850000.00'),
            direccion='Calle de prueba 789',
            ciudad='Saltillo',
            zona='Centro',
            latitud=Decimal('25.4383000'),
            longitud=Decimal('-100.9737000'),
            recamaras=3,
            banos=Decimal('2.0'),
            metros_construccion=Decimal('180.00'),
            metros_terreno=Decimal('220.00'),
            activo=False,
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Casa disponible')
        self.assertNotContains(response, 'Casa vendida')
        self.assertNotContains(response, 'Casa desactivada')
        self.assertContains(response, 'Imagen no disponible')

    def test_home_card_uses_only_the_principal_house_image(self):
        casa = Casa.objects.create(
            titulo='Casa con fotografías',
            descripcion='Casa de prueba',
            precio=Decimal('1850000.00'),
            direccion='Calle de prueba 123',
            ciudad='Saltillo',
            zona='Centro',
            latitud=Decimal('25.4383000'),
            longitud=Decimal('-100.9737000'),
            recamaras=3,
            banos=Decimal('2.0'),
            metros_construccion=Decimal('180.00'),
            metros_terreno=Decimal('220.00'),
        )
        Imagen.objects.create(
            casa=casa,
            ruta_imagen='casas/principal.jpg',
            es_principal=True,
        )
        Imagen.objects.create(
            casa=casa,
            ruta_imagen='casas/secundaria.jpg',
            es_principal=False,
        )

        response = self.client.get(reverse('home'))

        self.assertContains(response, '/media/casas/principal.jpg')
        self.assertNotContains(response, '/media/casas/secundaria.jpg')

    def test_search_filters_houses_by_city_and_maximum_price(self):
        Casa.objects.create(
            titulo='Casa en Saltillo',
            descripcion='Casa de prueba',
            precio=Decimal('1850000.00'),
            direccion='Calle de prueba 123',
            ciudad='Saltillo',
            zona='Centro',
            latitud=Decimal('25.4383000'),
            longitud=Decimal('-100.9737000'),
            recamaras=3,
            banos=Decimal('2.0'),
            metros_construccion=Decimal('180.00'),
            metros_terreno=Decimal('220.00'),
        )
        Casa.objects.create(
            titulo='Casa en Monterrey',
            descripcion='Otra casa de prueba',
            precio=Decimal('2850000.00'),
            direccion='Avenida de prueba 456',
            ciudad='Monterrey',
            zona='Centro',
            latitud=Decimal('25.6866000'),
            longitud=Decimal('-100.3161000'),
            recamaras=4,
            banos=Decimal('3.0'),
            metros_construccion=Decimal('220.00'),
            metros_terreno=Decimal('260.00'),
        )

        response = self.client.get(
            reverse('home'),
            {'buscar': '1', 'ciudad': 'Saltillo', 'precio_max': '2000000'},
        )

        self.assertContains(response, 'Casa en Saltillo')
        self.assertNotContains(response, 'Casa en Monterrey')

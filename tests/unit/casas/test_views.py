from decimal import Decimal
from io import BytesIO
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from PIL import Image as PillowImage

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
        self.assertContains(
            response,
            reverse('casa_detalle', args=[Casa.objects.get(titulo='Casa disponible').pk]),
        )
        self.assertNotContains(response, 'Casa vendida')
        self.assertNotContains(response, 'Casa desactivada')
        self.assertContains(response, 'Imagen no disponible')
        self.assertContains(response, 'id="heroMainCarousel"')
        self.assertContains(response, 'data-bs-ride="carousel"')
        self.assertContains(response, 'id="multicasaPromoVideo"')
        self.assertContains(response, 'assets/multimedia/multicasa-promocional.mp4')
        self.assertContains(response, 'id="multicasaPromoAudio"')
        self.assertContains(response, 'assets/multimedia/multicasa-guia-audio.mp3')

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
        self.assertContains(response, 'id="searchResultsMapIframe"')
        self.assertContains(response, 'maps.google.com/maps?q=25.4383000,-100.9737000')
        self.assertNotContains(response, '25.6866000')


class CasaDetailViewTests(TestCase):
    def crear_casa(self, **overrides):
        data = {
            'titulo': 'Casa de detalle',
            'descripcion': 'Descripción completa de la propiedad.',
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
        return Casa.objects.create(**data)

    def test_detail_shows_all_house_fields_google_map_and_contact_link(self):
        casa = self.crear_casa()
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

        response = self.client.get(reverse('casa_detalle', args=[casa.pk]))

        self.assertEqual(response.status_code, 200)
        for value in (
            'Casa de detalle',
            'Descripción completa de la propiedad.',
            'ID de registro',
            str(casa.pk),
            '1850000.00',
            'Calle de prueba 123',
            'Saltillo',
            'Centro',
            '25.4383000',
            '-100.9737000',
            '3',
            '2.0',
            '180.00',
            '220.00',
            'En venta',
            'Activa',
        ):
            with self.subTest(value=value):
                self.assertContains(response, value)
        self.assertContains(response, '/media/casas/principal.jpg')
        self.assertContains(response, '/media/casas/secundaria.jpg')
        self.assertContains(response, 'data-bs-ride="carousel"')
        self.assertContains(response, 'data-bs-interval="5000"')
        self.assertContains(response, 'data-bs-slide="prev"')
        self.assertContains(response, 'data-bs-slide="next"')
        self.assertEqual(
            response.content.decode().count('carousel-item active'),
            1,
        )
        self.assertContains(response, 'maps.google.com/maps?q=25.4383000,-100.9737000')
        self.assertContains(response, f'/contacto/?casa={casa.pk}')
        self.assertContains(response, reverse('casa_ficha_pdf', args=[casa.pk]))

    def test_inactive_house_detail_is_not_public(self):
        casa = self.crear_casa(activo=False)

        response = self.client.get(reverse('casa_detalle', args=[casa.pk]))

        self.assertEqual(response.status_code, 404)

    def test_single_image_does_not_show_carousel_controls(self):
        casa = self.crear_casa()
        Imagen.objects.create(
            casa=casa,
            ruta_imagen='casas/unica.jpg',
            es_principal=True,
        )

        response = self.client.get(reverse('casa_detalle', args=[casa.pk]))

        self.assertContains(response, '/media/casas/unica.jpg')
        self.assertNotContains(response, 'data-bs-slide="prev"')
        self.assertNotContains(response, 'data-bs-slide="next"')

    def test_ficha_pdf_downloads_valid_pdf_with_house_details(self):
        casa = self.crear_casa()

        response = self.client.get(reverse('casa_ficha_pdf', args=[casa.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            f'attachment; filename="ficha-casa-{casa.pk}.pdf"',
        )
        self.assertTrue(response.content.startswith(b'%PDF-1.4'))
        decoded_pdf = response.content.decode('cp1252', errors='ignore')
        for expected in (
            'BIENES RAÍCES MULTICASA',
            'Casa de detalle',
            'Calle de prueba 123',
            'Saltillo',
            'Centro',
            '1,850,000.00',
            '180.00 m2',
            '220.00 m2',
            'En venta',
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, decoded_pdf)

    def test_ficha_pdf_includes_house_images_in_a_gallery_page(self):
        image_bytes = BytesIO()
        PillowImage.new('RGB', (20, 10), color='blue').save(image_bytes, format='PNG')
        image_upload = SimpleUploadedFile(
            'fachada.png',
            image_bytes.getvalue(),
            content_type='image/png',
        )

        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            casa = self.crear_casa()
            Imagen.objects.create(casa=casa, ruta_imagen=image_upload, es_principal=True)
            Imagen.objects.create(
                casa=casa,
                ruta_imagen=SimpleUploadedFile(
                    'sala.png',
                    image_bytes.getvalue(),
                    content_type='image/png',
                ),
            )

            response = self.client.get(reverse('casa_ficha_pdf', args=[casa.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.count(b'/Subtype /Image'), 2)
        self.assertIn(b'/Count 2', response.content)
        self.assertIn(b'/Im1 Do', response.content)
        self.assertIn(b'/Im2 Do', response.content)

    def test_inactive_house_ficha_pdf_returns_404(self):
        casa = self.crear_casa(activo=False)

        response = self.client.get(reverse('casa_ficha_pdf', args=[casa.pk]))

        self.assertEqual(response.status_code, 404)

from decimal import Decimal
from io import BytesIO
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PillowImage

from apps.casas.models import Casa, Imagen


class PublicFunctionalWorkflowTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        media_override.enable()
        self.addCleanup(media_override.disable)

        self.casa = Casa.objects.create(
            titulo='Casa funcional',
            descripcion='Descripción visible en el flujo público.',
            precio=Decimal('1850000.00'),
            direccion='Calle Pruebas 123',
            ciudad='Saltillo',
            zona='Centro',
            latitud=Decimal('25.4383000'),
            longitud=Decimal('-100.9737000'),
            recamaras=3,
            banos=Decimal('2.0'),
            metros_construccion=Decimal('180.00'),
            metros_terreno=Decimal('220.00'),
        )
        image_bytes = BytesIO()
        PillowImage.new('RGB', (20, 10), color='blue').save(image_bytes, format='PNG')
        Imagen.objects.create(
            casa=self.casa,
            ruta_imagen=SimpleUploadedFile(
                'casa_funcional.png',
                image_bytes.getvalue(),
                content_type='image/png',
            ),
            es_principal=True,
        )

    def test_public_home_search_detail_and_pdf_flow(self):
        home = self.client.get(
            reverse('home'),
            {'buscar': '1', 'ciudad': 'Saltillo', 'precio_max': '2000000'},
        )
        self.assertEqual(home.status_code, 200)
        self.assertContains(home, 'Casa funcional')
        self.assertContains(home, '/media/casas/casa_funcional')
        self.assertContains(home, 'hero-casa-exterior-001')

        detail = self.client.get(reverse('casa_detalle', args=[self.casa.pk]))
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'Descripción visible en el flujo público.')
        self.assertContains(detail, f'/contacto/?casa={self.casa.pk}')

        pdf = self.client.get(reverse('casa_ficha_pdf', args=[self.casa.pk]))
        self.assertEqual(pdf.status_code, 200)
        self.assertTrue(pdf.content.startswith(b'%PDF-1.4'))
        self.assertContains(home, 'id="searchResultsMapIframe"')

    def test_mobile_navigation_and_search_markup_is_rendered(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'class="navbar-toggler"', html=False)
        self.assertContains(response, 'data-bs-toggle="collapse"', html=False)
        self.assertContains(response, 'name="viewport"', html=False)
        self.assertContains(response, '@media', count=0)

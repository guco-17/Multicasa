from decimal import Decimal
from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PillowImage

from apps.casas.models import Casa, Imagen
from apps.reportes.services import ReporteService


class DatabaseMapPdfReportDashboardTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        media_override.enable()
        self.addCleanup(media_override.disable)

        self.staff = get_user_model().objects.create_user(
            username='report-test-staff',
            password='test-password',
            is_staff=True,
        )
        self.venta = Casa.objects.create(
            titulo='Casa económica',
            descripcion='Prueba de persistencia',
            precio=Decimal('950000.00'),
            direccion='Av. Norte 100',
            ciudad='Saltillo',
            zona='Norte',
            latitud=Decimal('25.4500000'),
            longitud=Decimal('-100.9800000'),
            recamaras=2,
            banos=Decimal('1.0'),
            metros_construccion=Decimal('120.00'),
            metros_terreno=Decimal('150.00'),
        )
        self.vendida = Casa.objects.create(
            titulo='Casa residencial',
            descripcion='Prueba de reporte',
            precio=Decimal('3500000.00'),
            direccion='Av. Centro 200',
            ciudad='Monterrey',
            zona='Centro',
            latitud=Decimal('25.6866000'),
            longitud=Decimal('-100.3161000'),
            recamaras=5,
            banos=Decimal('4.5'),
            metros_construccion=Decimal('420.00'),
            metros_terreno=Decimal('600.00'),
            estatus='vendida',
        )

    def test_database_persists_and_cascade_deletes_images(self):
        imagen = Imagen.objects.create(
            casa=self.venta,
            ruta_imagen='casas/base_de_datos.jpg',
            es_principal=True,
        )
        image_id = imagen.pk
        self.assertTrue(Casa.objects.filter(pk=self.venta.pk).exists())
        self.assertTrue(Imagen.objects.filter(pk=image_id).exists())

        self.venta.delete()
        self.assertFalse(Imagen.objects.filter(pk=image_id).exists())

    def test_map_uses_saved_coordinates_and_updates_pin_data(self):
        response = self.client.get(
            reverse('home'),
            {'buscar': '1', 'ciudad': 'Saltillo'},
        )

        self.assertContains(response, 'maps.google.com/maps?q=25.4500000,-100.9800000')
        self.assertContains(response, 'data-lat="25.4500000"', html=False)
        self.assertContains(response, 'data-lng="-100.9800000"', html=False)

    def test_pdf_contains_property_and_download_headers(self):
        image_bytes = BytesIO()
        PillowImage.new('RGB', (20, 10), color='green').save(image_bytes, format='PNG')
        Imagen.objects.create(
            casa=self.venta,
            ruta_imagen=SimpleUploadedFile(
                'reporte.png',
                image_bytes.getvalue(),
                content_type='image/png',
            ),
            es_principal=True,
        )
        response = self.client.get(reverse('casa_ficha_pdf', args=[self.venta.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(
            response['Content-Disposition'],
            f'attachment; filename="ficha-casa-{self.venta.pk}.pdf"',
        )
        self.assertTrue(response.content.startswith(b'%PDF-1.4'))

    def test_report_and_dashboard_include_database_totals_and_filters(self):
        self.client.force_login(self.staff)

        report = self.client.get(reverse('reportes_exportar'))
        self.assertContains(report, 'Casa económica')
        self.assertContains(report, 'Casa residencial')
        self.assertEqual(report.context['total_casas'], 2)
        self.assertEqual(report.context['estatus']['en_venta'], 1)
        self.assertEqual(report.context['estatus']['vendida'], 1)

        sold_report = self.client.get(
            reverse('reportes_exportar'),
            {'estatus': 'vendida'},
        )
        self.assertContains(sold_report, 'Casa residencial')
        self.assertNotContains(sold_report, 'Casa económica')

        dashboard = self.client.get(reverse('dashboard'))
        self.assertContains(dashboard, 'chartRangosCosto')
        self.assertContains(dashboard, 'chartEstatusCasas')
        self.assertEqual(dashboard.context['rangos']['Económica'], 1)
        self.assertEqual(dashboard.context['rangos']['Residencial'], 1)

        conteo, _ = ReporteService.obtener_rangos_precios()
        self.assertEqual(conteo['Económica'], 1)
        self.assertEqual(conteo['Residencial'], 1)

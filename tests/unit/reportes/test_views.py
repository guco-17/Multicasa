from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.casas.models import Casa


class ReporteCasasViewTests(TestCase):
    def setUp(self):
        self.staff_user = get_user_model().objects.create_user(
            username='report-admin',
            password='test-password',
            is_staff=True,
        )
        self.casa_venta = Casa.objects.create(
            titulo='Casa Residencial Norte',
            descripcion='Casa en venta para reporte',
            precio=Decimal('1450000.00'),
            direccion='Av. Universidad 100',
            ciudad='Saltillo',
            zona='Norte',
            latitud=Decimal('25.4500000'),
            longitud=Decimal('-100.9800000'),
            recamaras=3,
            banos=Decimal('2.5'),
            metros_construccion=Decimal('190.00'),
            metros_terreno=Decimal('240.00'),
            estatus='en_venta',
            activo=True,
        )
        self.casa_vendida = Casa.objects.create(
            titulo='Casa Colonial Centro',
            descripcion='Casa vendida para reporte',
            precio=Decimal('950000.00'),
            direccion='Calle Hidalgo 200',
            ciudad='Saltillo',
            zona='Centro',
            latitud=Decimal('25.4200000'),
            longitud=Decimal('-101.0000000'),
            recamaras=2,
            banos=Decimal('1.0'),
            metros_construccion=Decimal('120.00'),
            metros_terreno=Decimal('150.00'),
            estatus='vendida',
            activo=False,
        )

    def test_reporte_requires_staff_user(self):
        response = self.client.get(reverse('reportes_exportar'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('reportes_exportar')}",
        )

        regular_user = get_user_model().objects.create_user(
            username='regular-visitor',
            password='test-password',
            is_staff=False,
        )
        self.client.force_login(regular_user)
        response = self.client.get(reverse('reportes_exportar'))
        self.assertEqual(response.status_code, 403)

    def test_reporte_lists_all_database_houses_with_their_status(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse('reportes_exportar'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Casa Residencial Norte')
        self.assertContains(response, 'En venta')
        self.assertContains(response, '1450000.00')
        self.assertContains(response, 'Casa Colonial Centro')
        self.assertContains(response, 'Vendida')
        self.assertContains(response, '950000.00')
        self.assertEqual(response.context['total_casas'], 2)
        self.assertEqual(response.context['estatus']['en_venta'], 1)
        self.assertEqual(response.context['estatus']['vendida'], 1)

    def test_reporte_filters_by_estatus(self):
        self.client.force_login(self.staff_user)

        response_venta = self.client.get(reverse('reportes_exportar'), {'estatus': 'en_venta'})
        self.assertContains(response_venta, 'Casa Residencial Norte')
        self.assertNotContains(response_venta, 'Casa Colonial Centro')

        response_vendida = self.client.get(reverse('reportes_exportar'), {'estatus': 'vendida'})
        self.assertContains(response_vendida, 'Casa Colonial Centro')
        self.assertNotContains(response_vendida, 'Casa Residencial Norte')


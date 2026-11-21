from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.casas.models import Casa


class CasaRestApiTests(APITestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_user(
            username='api-admin',
            password='test-password',
            is_staff=True,
        )
        self.regular_user = get_user_model().objects.create_user(
            username='api-user',
            password='test-password',
            is_staff=False,
        )
        self.casa_activa = Casa.objects.create(
            titulo='Casa API Activa',
            descripcion='Propiedad publicada en API REST',
            precio=Decimal('1950000.00'),
            direccion='Blvd. Venustiano Carranza 100',
            ciudad='Saltillo',
            zona='Norte',
            latitud=Decimal('25.4480000'),
            longitud=Decimal('-100.9760000'),
            recamaras=3,
            banos=Decimal('2.5'),
            metros_construccion=Decimal('185.00'),
            metros_terreno=Decimal('230.00'),
            estatus='en_venta',
            activo=True,
        )
        self.casa_inactiva = Casa.objects.create(
            titulo='Casa API Inactiva',
            descripcion='Propiedad oculta en API REST',
            precio=Decimal('1500000.00'),
            direccion='Calle Oculta 200',
            ciudad='Saltillo',
            zona='Sur',
            latitud=Decimal('25.4100000'),
            longitud=Decimal('-100.9900000'),
            recamaras=2,
            banos=Decimal('1.5'),
            metros_construccion=Decimal('130.00'),
            metros_terreno=Decimal('160.00'),
            estatus='en_venta',
            activo=False,
        )

    def payload_casa(self, **overrides):
        data = {
            'titulo': 'Casa Nueva desde API',
            'descripcion': 'Creada mediante endpoint POST',
            'precio': '2100000.00',
            'direccion': 'Av. Reforma 300',
            'ciudad': 'Monterrey',
            'zona': 'Centro',
            'latitud': '25.6866000',
            'longitud': '-100.3161000',
            'recamaras': 4,
            'banos': '3.0',
            'metros_construccion': '215.00',
            'metros_terreno': '280.00',
            'estatus': 'en_venta',
            'activo': True,
        }
        data.update(overrides)
        return data

    def test_public_can_list_and_retrieve_only_active_houses(self):
        list_url = reverse('casas-list')
        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titulos = [item['titulo'] for item in response.json()]
        self.assertIn('Casa API Activa', titulos)
        self.assertNotIn('Casa API Inactiva', titulos)

        detail_url = reverse('casas-detail', args=[self.casa_activa.pk])
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.json()['titulo'], 'Casa API Activa')

        inactive_url = reverse('casas-detail', args=[self.casa_inactiva.pk])
        inactive_response = self.client.get(inactive_url)
        self.assertEqual(inactive_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_write_operations_reject_anonymous_and_non_admin_users(self):
        list_url = reverse('casas-list')
        detail_url = reverse('casas-detail', args=[self.casa_activa.pk])

        for user in (None, self.regular_user):
            if user:
                self.client.force_authenticate(user=user)
            else:
                self.client.force_authenticate(user=None)

            self.assertEqual(
                self.client.post(list_url, self.payload_casa(), format='json').status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(detail_url, {'estatus': 'vendida'}, format='json').status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

    def test_admin_can_create_update_and_delete_houses_via_api(self):
        self.client.force_authenticate(user=self.admin_user)
        list_url = reverse('casas-list')

        create_response = self.client.post(list_url, self.payload_casa(), format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        created_id = create_response.json()['id']
        self.assertTrue(Casa.objects.filter(pk=created_id, titulo='Casa Nueva desde API').exists())

        detail_url = reverse('casas-detail', args=[created_id])
        patch_response = self.client.patch(
            detail_url,
            {'estatus': 'vendida', 'precio': '2050000.00'},
            format='json',
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        casa = Casa.objects.get(pk=created_id)
        self.assertEqual(casa.estatus, 'vendida')
        self.assertEqual(casa.precio, Decimal('2050000.00'))

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Casa.objects.filter(pk=created_id).exists())


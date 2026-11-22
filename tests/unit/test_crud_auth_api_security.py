from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.casas.models import Casa


class CrudAndAuthenticationSecurityTests(TestCase):
    def casa_data(self, **overrides):
        data = {
            'titulo': 'Casa segura',
            'descripcion': 'Datos de prueba',
            'precio': '1750000.00',
            'direccion': 'Calle Seguridad 10',
            'ciudad': 'Saltillo',
            'zona': 'Centro',
            'latitud': '25.4383000',
            'longitud': '-100.9737000',
            'recamaras': '3',
            'banos': '2.0',
            'metros_construccion': '180.00',
            'metros_terreno': '220.00',
            'estatus': 'en_venta',
            'activo': 'on',
        }
        data.update(overrides)
        return data

    def test_crud_requires_authentication_and_role_permissions(self):
        anonymous = self.client.get(reverse('gestion:casas'))
        self.assertRedirects(
            anonymous,
            f"{reverse('login')}?next={reverse('gestion:casas')}",
        )

        regular = get_user_model().objects.create_user(
            username='regular-security',
            password='test-password',
        )
        self.client.force_login(regular)
        self.assertEqual(
            self.client.get(reverse('gestion:casas')).status_code,
            403,
        )

    def test_superuser_create_update_delete_flow(self):
        admin = get_user_model().objects.create_superuser(
            username='security-admin',
            email='security-admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin)

        create = self.client.post(
            reverse('gestion:casa_crear'),
            self.casa_data(),
        )
        self.assertRedirects(create, reverse('gestion:casas'))
        casa = Casa.objects.get(titulo='Casa segura')

        update = self.client.post(
            reverse('gestion:casa_editar', args=[casa.pk]),
            self.casa_data(titulo='Casa segura actualizada'),
        )
        self.assertRedirects(update, reverse('gestion:casas'))
        casa.refresh_from_db()
        self.assertEqual(casa.titulo, 'Casa segura actualizada')

        delete = self.client.post(reverse('gestion:casa_eliminar', args=[casa.pk]))
        self.assertRedirects(delete, reverse('gestion:casas'))
        self.assertFalse(Casa.objects.filter(pk=casa.pk).exists())

    def test_search_input_is_not_returned_as_unescaped_script(self):
        payload = '<script>alert("xss")</script>'
        response = self.client.get(reverse('home'), {'buscar': '1', 'ciudad': payload})

        self.assertNotContains(response, payload)
        self.assertContains(response, '&lt;script&gt;')


class CasaApiSecurityTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username='api-security-admin',
            email='api-security-admin@example.com',
            password='test-password',
        )
        self.regular = get_user_model().objects.create_user(
            username='api-security-user',
            password='test-password',
        )

    def payload(self, **overrides):
        data = {
            'titulo': 'Casa API segura',
            'descripcion': 'Creada para prueba de seguridad',
            'precio': '1950000.00',
            'direccion': 'Av. Seguridad 20',
            'ciudad': 'Monterrey',
            'zona': 'Centro',
            'latitud': '25.6866000',
            'longitud': '-100.3161000',
            'recamaras': 3,
            'banos': '2.5',
            'metros_construccion': '185.00',
            'metros_terreno': '230.00',
            'estatus': 'en_venta',
            'activo': True,
        }
        data.update(overrides)
        return data

    def test_public_read_is_allowed_but_writes_require_admin(self):
        self.assertEqual(
            self.client.get(reverse('casas-list')).status_code,
            200,
        )

        list_url = reverse('casas-list')
        for user in (None, self.regular):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(list_url, self.payload(), format='json').status_code,
                403,
            )

    def test_admin_crud_and_csrf_protection(self):
        self.client.force_authenticate(user=self.admin)
        list_url = reverse('casas-list')
        created = self.client.post(list_url, self.payload(), format='json')
        self.assertEqual(created.status_code, 201)
        casa_id = created.json()['id']

        detail_url = reverse('casas-detail', args=[casa_id])
        patched = self.client.patch(detail_url, {'estatus': 'vendida'}, format='json')
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(Casa.objects.get(pk=casa_id).estatus, 'vendida')

        deleted = self.client.delete(detail_url)
        self.assertEqual(deleted.status_code, 204)
        self.assertFalse(Casa.objects.filter(pk=casa_id).exists())

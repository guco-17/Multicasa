from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.casas.models import Casa, Imagen
from apps.contacto.models import MensajeContacto


class AdminCrudTests(TestCase):
    def test_all_project_models_are_registered_for_admin_crud(self):
        for model in (Casa, Imagen, MensajeContacto):
            with self.subTest(model=model.__name__):
                self.assertIn(model, admin.site._registry)

    def test_admin_crud_requires_staff_access(self):
        response = self.client.get(reverse('admin:casas_casa_changelist'))
        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={reverse('admin:casas_casa_changelist')}",
        )

        user = get_user_model().objects.create_user(
            username='regular-user',
            password='test-password',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('admin:casas_casa_changelist'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.split('?')[0], reverse('admin:login'))

    def test_superuser_can_open_each_registered_model(self):
        user = get_user_model().objects.create_superuser(
            username='admin-test',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(user)

        for model in (Casa, Imagen, MensajeContacto):
            with self.subTest(model=model.__name__):
                response = self.client.get(
                    reverse(f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist')
                )
                self.assertEqual(response.status_code, 200)

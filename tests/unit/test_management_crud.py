from io import BytesIO
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image as PillowImage

from apps.casas.models import Casa, Imagen
from apps.contacto.models import MensajeContacto


class ManagementCrudTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        media_override.enable()
        self.addCleanup(media_override.disable)

    def login_as_superuser(self):
        user = get_user_model().objects.create_superuser(
            username='management-admin',
            email='management-admin@example.com',
            password='test-password',
        )
        self.client.force_login(user)

    def casa_data(self, **overrides):
        data = {
            'titulo': 'Casa de prueba',
            'descripcion': 'Descripción de prueba',
            'precio': '1850000.00',
            'direccion': 'Calle de prueba 123',
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

    @staticmethod
    def image_upload():
        image_bytes = BytesIO()
        PillowImage.new('RGB', (1, 1), color='blue').save(image_bytes, format='PNG')
        return SimpleUploadedFile(
            'fachada.png',
            image_bytes.getvalue(),
            content_type='image/png',
        )

    def test_management_requires_staff_and_model_permissions(self):
        response = self.client.get(reverse('gestion:casas'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('gestion:casas')}",
        )

        staff_user = get_user_model().objects.create_user(
            username='staff-without-permissions',
            password='test-password',
            is_staff=True,
        )
        self.client.force_login(staff_user)
        response = self.client.get(reverse('gestion:casas'))
        self.assertEqual(response.status_code, 403)

    def test_staff_model_permissions_control_available_actions(self):
        staff_user = get_user_model().objects.create_user(
            username='catalog-reader',
            password='test-password',
            is_staff=True,
        )
        permission = Permission.objects.get(
            content_type=ContentType.objects.get(
                app_label='casas',
                model='casa',
            ),
            codename='view_casa',
        )
        staff_user.user_permissions.add(permission)
        self.client.force_login(staff_user)

        response = self.client.get(reverse('gestion:casas'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('gestion:casa_crear'))
        self.assertEqual(
            self.client.get(reverse('gestion:casa_crear')).status_code,
            403,
        )

    def test_non_staff_login_returns_to_public_home(self):
        get_user_model().objects.create_user(
            username='regular-user',
            password='test-password',
        )

        response = self.client.post(
            reverse('login'),
            {'username': 'regular-user', 'password': 'test-password'},
        )

        self.assertRedirects(response, reverse('home'))

    def test_superuser_can_use_crud_for_every_management_model(self):
        self.login_as_superuser()

        dashboard = self.client.get(reverse('dashboard'))
        self.assertContains(dashboard, reverse('gestion:casas'))
        self.assertContains(dashboard, reverse('gestion:imagenes'))
        self.assertContains(dashboard, reverse('gestion:mensajes'))

        casa_url = reverse('gestion:casa_crear')
        response = self.client.post(casa_url, self.casa_data())
        self.assertRedirects(response, reverse('gestion:casas'))
        casa = Casa.objects.get(titulo='Casa de prueba')

        response = self.client.get(reverse('gestion:casas'))
        self.assertContains(response, 'Casa de prueba')
        self.assertContains(response, reverse('gestion:casa_editar', args=[casa.pk]))
        response = self.client.post(
            reverse('gestion:casa_editar', args=[casa.pk]),
            self.casa_data(titulo='Casa actualizada'),
        )
        self.assertRedirects(response, reverse('gestion:casas'))
        casa.refresh_from_db()
        self.assertEqual(casa.titulo, 'Casa actualizada')

        imagen_url = reverse('gestion:imagen_crear')
        response = self.client.post(
            imagen_url,
            {
                'casa': casa.pk,
                'ruta_imagen': self.image_upload(),
                'es_principal': 'on',
            },
        )
        self.assertRedirects(response, reverse('gestion:imagenes'))
        imagen = Imagen.objects.get(casa=casa)

        response = self.client.get(reverse('gestion:imagenes'))
        self.assertContains(response, 'fachada.png')
        response = self.client.post(
            reverse('gestion:imagen_editar', args=[imagen.pk]),
            {'casa': casa.pk, 'es_principal': ''},
        )
        self.assertRedirects(response, reverse('gestion:imagenes'))
        imagen.refresh_from_db()
        self.assertFalse(imagen.es_principal)

        mensaje_url = reverse('gestion:mensaje_crear')
        response = self.client.post(
            mensaje_url,
            {
                'casa': casa.pk,
                'nombre': 'Visitante',
                'correo': 'visitante@example.com',
                'telefono': '8441234567',
                'mensaje': 'Solicito información.',
            },
        )
        self.assertRedirects(response, reverse('gestion:mensajes'))
        mensaje = MensajeContacto.objects.get(nombre='Visitante')

        response = self.client.post(
            reverse('gestion:mensaje_editar', args=[mensaje.pk]),
            {
                'casa': casa.pk,
                'nombre': 'Visitante actualizado',
                'correo': 'visitante@example.com',
                'telefono': '8441234567',
                'mensaje': 'Mensaje actualizado.',
            },
        )
        self.assertRedirects(response, reverse('gestion:mensajes'))
        mensaje.refresh_from_db()
        self.assertEqual(mensaje.nombre, 'Visitante actualizado')

        for model, delete_name, list_name in (
            (Imagen, 'gestion:imagen_eliminar', 'gestion:imagenes'),
            (MensajeContacto, 'gestion:mensaje_eliminar', 'gestion:mensajes'),
            (Casa, 'gestion:casa_eliminar', 'gestion:casas'),
        ):
            obj = model.objects.first()
            response = self.client.post(reverse(delete_name, args=[obj.pk]))
            self.assertRedirects(response, reverse(list_name))
            self.assertFalse(model.objects.filter(pk=obj.pk).exists())

        self.assertIsNone(MensajeContacto.objects.first())

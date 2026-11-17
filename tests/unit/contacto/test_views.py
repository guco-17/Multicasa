from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.casas.models import Casa
from apps.contacto.models import MensajeContacto


class ContactoFormViewTests(TestCase):
    def setUp(self):
        self.casa_disponible = self.crear_casa('Casa disponible')
        self.casa_vendida = self.crear_casa('Casa vendida', estatus='vendida')
        self.casa_inactiva = self.crear_casa('Casa inactiva', activo=False)

    def crear_casa(self, titulo, **overrides):
        data = {
            'titulo': titulo,
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
        return Casa.objects.create(**data)

    def contacto_data(self, **overrides):
        data = {
            'nombre': 'Visitante de prueba',
            'correo': 'visitante@example.com',
            'telefono': '8441234567',
            'mensaje': 'Me gustaría recibir información.',
        }
        data.update(overrides)
        return data

    @staticmethod
    def casa_label(casa):
        return f'{casa.titulo} — {casa.direccion}, {casa.ciudad}'

    def test_form_offers_only_active_houses_for_sale(self):
        response = self.client.get(reverse('contacto'))

        self.assertContains(response, 'Casa que te interesa (opcional)')
        self.assertContains(response, 'Escribe el nombre o la dirección')

    def test_contact_link_can_prefill_the_selected_house(self):
        response = self.client.get(
            reverse('contacto'),
            {'casa': self.casa_disponible.pk},
        )

        self.assertContains(response, 'name="casa"')
        self.assertContains(response, f'value="{self.casa_disponible.pk}"')
        self.assertContains(response, self.casa_label(self.casa_disponible))

    def test_house_search_matches_name_or_address_and_only_returns_available_houses(self):
        response = self.client.get(
            reverse('contacto_casas_buscar'),
            {'q': 'Casa disponible'},
        )
        self.assertEqual(
            [house['id'] for house in response.json()['results']],
            [self.casa_disponible.pk],
        )

        response = self.client.get(
            reverse('contacto_casas_buscar'),
            {'q': 'Calle de prueba'},
        )
        self.assertEqual(
            [house['id'] for house in response.json()['results']],
            [self.casa_disponible.pk],
        )

    def test_contact_can_be_submitted_without_a_house(self):
        response = self.client.post(reverse('contacto'), self.contacto_data())

        self.assertRedirects(response, '/contacto/?success=1')
        mensaje = MensajeContacto.objects.get()
        self.assertIsNone(mensaje.casa)

    def test_selected_house_is_saved_with_the_contact(self):
        response = self.client.post(
            reverse('contacto'),
            self.contacto_data(
                casa=self.casa_disponible.pk,
                casa_busqueda=self.casa_label(self.casa_disponible),
            ),
        )

        self.assertRedirects(response, '/contacto/?success=1')
        mensaje = MensajeContacto.objects.get()
        self.assertEqual(mensaje.casa, self.casa_disponible)

    def test_sold_or_inactive_house_cannot_be_submitted(self):
        for casa in (self.casa_vendida, self.casa_inactiva):
            with self.subTest(casa=casa.titulo):
                response = self.client.post(
                    reverse('contacto'),
                    self.contacto_data(
                        casa=casa.pk,
                        casa_busqueda=self.casa_label(casa),
                    ),
                )
                self.assertEqual(response.status_code, 200)

        self.assertFalse(MensajeContacto.objects.exists())

    def test_typed_text_without_selecting_a_search_result_is_rejected(self):
        response = self.client.post(
            reverse('contacto'),
            self.contacto_data(casa_busqueda='Casa disponible'),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Selecciona una propiedad de los resultados de búsqueda.',
        )
        self.assertFalse(MensajeContacto.objects.exists())

from decimal import Decimal

from django.test import TestCase

from apps.casas.models import Casa
from apps.contacto.models import MensajeContacto


class MensajeContactoModelTests(TestCase):
    def test_contact_message_can_be_general(self):
        mensaje = MensajeContacto.objects.create(
            nombre='Visitante de prueba',
            correo='visitante@example.com',
            mensaje='Solicito información general.',
        )

        self.assertIsNone(mensaje.casa)

    def test_contact_message_is_preserved_when_house_is_deleted(self):
        casa = Casa.objects.create(
            titulo='Casa de prueba',
            descripcion='Descripción de prueba',
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
        mensaje = MensajeContacto.objects.create(
            casa=casa,
            nombre='Visitante de prueba',
            correo='visitante@example.com',
            mensaje='Me interesa esta casa.',
        )

        casa.delete()

        mensaje.refresh_from_db()
        self.assertIsNone(mensaje.casa)

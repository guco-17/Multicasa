from django.db import models

from apps.casas.models import Casa


class MensajeContacto(models.Model):
    casa = models.ForeignKey(Casa, on_delete=models.SET_NULL, null=True, blank=True, related_name='mensajes_contacto')
    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'

    def __str__(self):
        return f'{self.nombre} <{self.correo}>'

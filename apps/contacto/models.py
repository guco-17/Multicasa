from django.db import models

from apps.casas.models import Casa


class MensajeContacto(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_mensaje')
    casa = models.ForeignKey(
        Casa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensajes_contacto',
        db_column='id_casa',
    )
    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mensaje_contacto'
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'
        indexes = [
            models.Index(fields=['casa'], name='mensaje_casa_idx'),
            models.Index(fields=['fecha_envio'], name='mensaje_fecha_idx'),
        ]

    def __str__(self):
        return f'{self.nombre} <{self.correo}>'

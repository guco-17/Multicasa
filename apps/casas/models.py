from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Casa(models.Model):
    ESTATUS_CHOICES = (
        ('en_venta', 'En venta'),
        ('vendida', 'Vendida'),
    )

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    direccion = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100)
    zona = models.CharField(max_length=100)
    latitud = models.DecimalField(max_digits=10, decimal_places=7, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitud = models.DecimalField(max_digits=10, decimal_places=7, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    recamaras = models.PositiveSmallIntegerField()
    banos = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(Decimal('0.0'))])
    metros_construccion = models.DecimalField(max_digits=10, decimal_places=2)
    metros_terreno = models.DecimalField(max_digits=10, decimal_places=2)
    estatus = models.CharField(max_length=15, choices=ESTATUS_CHOICES, default='en_venta')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Casa'
        verbose_name_plural = 'Casas'

    def __str__(self):
        return f'{self.titulo} ({self.ciudad})'


class Imagen(models.Model):
    casa = models.ForeignKey(Casa, on_delete=models.CASCADE, related_name='imagenes')
    archivo = models.ImageField(upload_to='casas/')
    es_principal = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imágenes'

    def __str__(self):
        return f'Imagen de {self.casa_id}'


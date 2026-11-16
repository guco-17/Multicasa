from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Casa(models.Model):
    ESTATUS_CHOICES = (
        ('en_venta', 'En venta'),
        ('vendida', 'Vendida'),
    )

    id = models.AutoField(primary_key=True, db_column='id_casa')
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
        db_table = 'casa'
        ordering = ['-fecha_registro']
        verbose_name = 'Casa'
        verbose_name_plural = 'Casas'
        indexes = [
            models.Index(fields=['ciudad'], name='casa_ciudad_idx'),
            models.Index(fields=['estatus'], name='casa_estatus_idx'),
            models.Index(fields=['precio'], name='casa_precio_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(precio__gt=0),
                name='casa_precio_positivo',
            ),
            models.CheckConstraint(
                condition=models.Q(estatus__in=['en_venta', 'vendida']),
                name='casa_estatus_valido',
            ),
            models.CheckConstraint(
                condition=models.Q(latitud__gte=-90, latitud__lte=90),
                name='casa_latitud_valida',
            ),
            models.CheckConstraint(
                condition=models.Q(longitud__gte=-180, longitud__lte=180),
                name='casa_longitud_valida',
            ),
            models.CheckConstraint(
                condition=models.Q(banos__gte=0),
                name='casa_banos_no_negativos',
            ),
        ]

    def __str__(self):
        return f'{self.titulo} ({self.ciudad})'


class Imagen(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_imagen')
    casa = models.ForeignKey(
        Casa,
        on_delete=models.CASCADE,
        related_name='imagenes',
        db_column='id_casa',
    )
    ruta_imagen = models.ImageField(upload_to='casas/', max_length=255)
    es_principal = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'imagen'
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imágenes'
        indexes = [
            models.Index(fields=['casa'], name='imagen_casa_idx'),
        ]

    def __str__(self):
        return f'Imagen de {self.casa_id}'


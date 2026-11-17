from django.contrib import admin

from apps.contacto.models import MensajeContacto


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'casa', 'fecha_envio')
    list_filter = ('fecha_envio',)
    search_fields = ('nombre', 'correo', 'telefono', 'mensaje', 'casa__titulo')
    readonly_fields = ('fecha_envio',)

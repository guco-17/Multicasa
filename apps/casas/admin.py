from django.contrib import admin

from apps.casas.models import Casa, Imagen


class ImagenInline(admin.TabularInline):
    model = Imagen
    extra = 1


@admin.register(Casa)
class CasaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ciudad', 'zona', 'precio', 'estatus', 'activo')
    list_filter = ('estatus', 'activo', 'ciudad')
    search_fields = ('titulo', 'direccion', 'ciudad', 'zona')
    inlines = (ImagenInline,)


@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = ('casa', 'ruta_imagen', 'es_principal', 'fecha_registro')
    list_filter = ('es_principal', 'fecha_registro')
    search_fields = ('casa__titulo', 'casa__ciudad', 'ruta_imagen')
    autocomplete_fields = ('casa',)
    readonly_fields = ('fecha_registro',)

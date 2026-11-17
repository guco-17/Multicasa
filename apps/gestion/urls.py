from django.urls import path

from .views import (
    CasaCreateView,
    CasaDeleteView,
    CasaListView,
    CasaUpdateView,
    ImagenCreateView,
    ImagenDeleteView,
    ImagenListView,
    ImagenUpdateView,
    MensajeContactoCreateView,
    MensajeContactoDeleteView,
    MensajeContactoListView,
    MensajeContactoUpdateView,
)

app_name = 'gestion'

urlpatterns = [
    path('casas/', CasaListView.as_view(), name='casas'),
    path('casas/nueva/', CasaCreateView.as_view(), name='casa_crear'),
    path('casas/<int:pk>/editar/', CasaUpdateView.as_view(), name='casa_editar'),
    path('casas/<int:pk>/eliminar/', CasaDeleteView.as_view(), name='casa_eliminar'),
    path('imagenes/', ImagenListView.as_view(), name='imagenes'),
    path('imagenes/nueva/', ImagenCreateView.as_view(), name='imagen_crear'),
    path('imagenes/<int:pk>/editar/', ImagenUpdateView.as_view(), name='imagen_editar'),
    path('imagenes/<int:pk>/eliminar/', ImagenDeleteView.as_view(), name='imagen_eliminar'),
    path('mensajes/', MensajeContactoListView.as_view(), name='mensajes'),
    path('mensajes/nuevo/', MensajeContactoCreateView.as_view(), name='mensaje_crear'),
    path(
        'mensajes/<int:pk>/editar/',
        MensajeContactoUpdateView.as_view(),
        name='mensaje_editar',
    ),
    path(
        'mensajes/<int:pk>/eliminar/',
        MensajeContactoDeleteView.as_view(),
        name='mensaje_eliminar',
    ),
]

from django.urls import path

from .views import ContactoFormView, buscar_casas

urlpatterns = [
    path('contacto/', ContactoFormView.as_view(), name='contacto'),
    path('contacto/casas/buscar/', buscar_casas, name='contacto_casas_buscar'),
]

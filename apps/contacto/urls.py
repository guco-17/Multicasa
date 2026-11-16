from django.urls import path

from .views import ContactoFormView

urlpatterns = [
    path('contacto/', ContactoFormView.as_view(), name='contacto'),
]

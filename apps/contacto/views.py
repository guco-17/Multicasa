from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_GET
from django.views.generic import FormView

from apps.casas.models import Casa

from .forms import ContactoForm


@require_GET
def buscar_casas(request):
    query = request.GET.get('q', '').strip()[:150]
    casas = Casa.objects.none()
    if len(query) >= 2:
        casas = Casa.objects.filter(
            activo=True,
            estatus='en_venta',
        ).filter(
            Q(titulo__icontains=query) | Q(direccion__icontains=query)
        ).order_by('titulo')[:10]

    return JsonResponse({
        'results': [
            {
                'id': casa.pk,
                'title': casa.titulo,
                'address': casa.direccion,
                'city': casa.ciudad,
                'label': f'{casa.titulo} — {casa.direccion}, {casa.ciudad}',
            }
            for casa in casas
        ]
    })


class ContactoFormView(FormView):
    template_name = 'contacto/contacto.html'
    form_class = ContactoForm
    success_url = '/contacto/?success=1'

    def get_initial(self):
        initial = super().get_initial()
        casa_id = self.request.GET.get('casa', '')
        casa = None
        if casa_id.isdecimal() and len(casa_id) <= 10:
            casa = Casa.objects.filter(
                pk=casa_id,
                activo=True,
                estatus='en_venta',
            ).first()
        if casa:
            initial['casa'] = casa.pk
            initial['casa_busqueda'] = (
                f'{casa.titulo} — {casa.direccion}, {casa.ciudad}'
            )
        return initial

    def form_valid(self, form):
        form.save()
        send_mail(
            subject='Nuevo mensaje de contacto - Multicasa',
            message=form.cleaned_data['mensaje'],
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )
        return redirect(self.success_url)

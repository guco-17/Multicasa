from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.generic import FormView

from .forms import ContactoForm


class ContactoFormView(FormView):
    template_name = 'contacto/contacto.html'
    form_class = ContactoForm
    success_url = '/contacto/?success=1'

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

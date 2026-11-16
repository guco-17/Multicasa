from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import TemplateView
from rest_framework import permissions, viewsets

from .forms import CasaBusquedaForm
from .models import Casa
from .serializers import CasaSerializer


class HomeView(TemplateView):
    template_name = 'casas/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_performed = 'buscar' in self.request.GET
        form = CasaBusquedaForm(self.request.GET if search_performed else None)
        casas = Casa.objects.none()

        if search_performed and form.is_valid():
            filters = form.cleaned_data
            casas = Casa.objects.filter(activo=True)

            if filters['ciudad']:
                casas = casas.filter(
                    Q(ciudad__icontains=filters['ciudad'])
                    | Q(zona__icontains=filters['ciudad'])
                )
            if filters['estatus']:
                casas = casas.filter(estatus=filters['estatus'])
            if filters['precio_min'] is not None:
                casas = casas.filter(precio__gte=filters['precio_min'])
            if filters['precio_max'] is not None:
                casas = casas.filter(precio__lte=filters['precio_max'])
            if filters['recamaras'] is not None:
                casas = casas.filter(recamaras__gte=filters['recamaras'])
            if filters['banos'] is not None:
                casas = casas.filter(banos__gte=filters['banos'])

        context['search_form'] = form
        context['search_performed'] = search_performed
        context['casas'] = casas[:12]
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'casas/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        casas = Casa.objects.all()
        context['total_casas'] = casas.count()
        context['casas_en_venta'] = casas.filter(estatus='en_venta').count()
        context['casas_vendidas'] = casas.filter(estatus='vendida').count()
        return context


class CasaViewSet(viewsets.ModelViewSet):
    queryset = Casa.objects.filter(activo=True)
    serializer_class = CasaSerializer

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

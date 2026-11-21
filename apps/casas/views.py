from django.db.models import Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import DetailView, TemplateView
from rest_framework import permissions, viewsets

from apps.gestion.mixins import StaffRequiredMixin
from apps.reportes.services import ReporteService

from .forms import CasaBusquedaForm
from .models import Casa, Imagen
from .pdf import build_casa_ficha_pdf
from .serializers import CasaSerializer


class HomeView(TemplateView):
    template_name = 'casas/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_performed = 'buscar' in self.request.GET
        form = CasaBusquedaForm(self.request.GET if search_performed else None)
        casas_publicadas = Casa.objects.filter(activo=True).prefetch_related(
            Prefetch(
                'imagenes',
                queryset=Imagen.objects.filter(es_principal=True).order_by('pk'),
                to_attr='imagenes_principales',
            )
        )
        casas = casas_publicadas.filter(estatus='en_venta')

        if search_performed and form.is_valid():
            filters = form.cleaned_data
            casas = casas_publicadas

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
        context['casas'] = casas
        return context


class CasaDetailView(DetailView):
    model = Casa
    template_name = 'casas/detail.html'
    context_object_name = 'casa'

    def get_queryset(self):
        return Casa.objects.filter(activo=True).prefetch_related(
            Prefetch(
                'imagenes',
                queryset=Imagen.objects.order_by('-es_principal', 'pk'),
            )
        )


class CasaFichaPDFView(View):
    def get(self, request, pk):
        casa = get_object_or_404(Casa, pk=pk, activo=True)
        pdf_bytes = build_casa_ficha_pdf(casa)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ficha-casa-{casa.pk}.pdf"'
        return response


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'casas/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datos_dashboard = ReporteService.obtener_datos_dashboard()
        context.update(datos_dashboard)
        context['casas_en_venta'] = datos_dashboard['estatus']['en_venta']
        context['casas_vendidas'] = datos_dashboard['estatus']['vendida']
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

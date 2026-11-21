from django.views.generic import TemplateView

from apps.casas.models import Casa
from apps.gestion.mixins import StaffRequiredMixin

from .services import ReporteService


class DashboardReportView(StaffRequiredMixin, TemplateView):
    template_name = 'reportes/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rangos'] = dict(ReporteService.obtener_rangos_precios()[0])
        context['estatus'] = ReporteService.obtener_estatus()
        return context


class ReporteCasasView(StaffRequiredMixin, TemplateView):
    template_name = 'reportes/reporte.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        estatus_filtro = self.request.GET.get('estatus', '').strip()
        if estatus_filtro not in {'en_venta', 'vendida'}:
            estatus_filtro = ''

        casas = ReporteService.obtener_listado_casas(estatus=estatus_filtro or None)
        estatus_conteo = ReporteService.obtener_estatus()

        context['casas'] = casas
        context['estatus_filtro'] = estatus_filtro
        context['estatus_choices'] = Casa.ESTATUS_CHOICES
        context['rangos'] = dict(ReporteService.obtener_rangos_precios()[0])
        context['estatus'] = estatus_conteo
        context['total_casas'] = estatus_conteo['en_venta'] + estatus_conteo['vendida']
        return context


exportar_reporte = ReporteCasasView.as_view()

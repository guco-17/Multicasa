from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from .services import ReporteService


@method_decorator(login_required, name='dispatch')
class DashboardReportView(TemplateView):
    template_name = 'reportes/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rangos'] = ReporteService.obtener_rangos_precios()[0]
        context['estatus'] = ReporteService.obtener_estatus()
        return context


def exportar_reporte(request):
    context = {
        'rangos': ReporteService.obtener_rangos_precios()[0],
        'estatus': ReporteService.obtener_estatus(),
    }
    return render(request, 'reportes/reporte.html', context)

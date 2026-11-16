from django.urls import path

from .views import DashboardReportView, exportar_reporte

urlpatterns = [
    path('reportes/', DashboardReportView.as_view(), name='reportes'),
    path('reportes/exportar/', exportar_reporte, name='reportes_exportar'),
]

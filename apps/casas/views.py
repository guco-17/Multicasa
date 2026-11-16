from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView
from rest_framework import permissions, viewsets

from .models import Casa
from .serializers import CasaSerializer


class HomeView(TemplateView):
    template_name = 'casas/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['casas'] = Casa.objects.filter(activo=True)[:6]
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

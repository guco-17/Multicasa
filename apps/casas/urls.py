from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CasaDetailView, CasaFichaPDFView, CasaViewSet, DashboardView, HomeView

router = DefaultRouter()
router.register(r'casas', CasaViewSet, basename='casas')

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('casas/<int:pk>/', CasaDetailView.as_view(), name='casa_detalle'),
    path('casas/<int:pk>/ficha-pdf/', CasaFichaPDFView.as_view(), name='casa_ficha_pdf'),
    path('api/v1/', include(router.urls)),
]

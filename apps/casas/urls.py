from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CasaViewSet, DashboardView, HomeView

router = DefaultRouter()
router.register(r'casas', CasaViewSet, basename='casas')

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('api/v1/', include(router.urls)),
]

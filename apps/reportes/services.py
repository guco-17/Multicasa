from collections import Counter

from apps.casas.models import Casa


class ReporteService:
    @staticmethod
    def obtener_rangos_precios(solo_activas=False):
        rangos = {
            'Económica': 0,
            'Media': 1000001,
            'Residencial': 2500001,
        }
        casas = Casa.objects.filter(activo=True) if solo_activas else Casa.objects.all()
        conteo = Counter({'Económica': 0, 'Media': 0, 'Residencial': 0})
        for casa in casas:
            if casa.precio <= 1000000:
                conteo['Económica'] += 1
            elif casa.precio <= 2500000:
                conteo['Media'] += 1
            else:
                conteo['Residencial'] += 1
        return conteo, rangos

    @staticmethod
    def obtener_estatus(solo_activas=False):
        casas = Casa.objects.filter(activo=True) if solo_activas else Casa.objects.all()
        return {
            'en_venta': casas.filter(estatus='en_venta').count(),
            'vendida': casas.filter(estatus='vendida').count(),
        }

    @staticmethod
    def obtener_listado_casas(estatus=None):
        queryset = Casa.objects.all().order_by('-fecha_registro', '-pk')
        if estatus in {'en_venta', 'vendida'}:
            queryset = queryset.filter(estatus=estatus)
        return queryset

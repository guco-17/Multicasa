from collections import Counter

from apps.casas.models import Casa


class ReporteService:
    @staticmethod
    def obtener_rangos_precios():
        rangos = {
            'Económica': 0,
            'Media': 1000001,
            'Residencial': 2500001,
        }
        casas = Casa.objects.filter(activo=True)
        conteo = Counter()
        for casa in casas:
            if casa.precio <= 1000000:
                conteo['Económica'] += 1
            elif casa.precio <= 2500000:
                conteo['Media'] += 1
            else:
                conteo['Residencial'] += 1
        return conteo, rangos

    @staticmethod
    def obtener_estatus():
        casas = Casa.objects.filter(activo=True)
        return {
            'en_venta': casas.filter(estatus='en_venta').count(),
            'vendida': casas.filter(estatus='vendida').count(),
        }

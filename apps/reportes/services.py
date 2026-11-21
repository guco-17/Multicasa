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

    @classmethod
    def obtener_datos_dashboard(cls, solo_activas=False):
        conteo_rangos, _ = cls.obtener_rangos_precios(solo_activas=solo_activas)
        estatus = cls.obtener_estatus(solo_activas=solo_activas)
        total = estatus['en_venta'] + estatus['vendida']

        etiquetas_rangos = {
            'Económica': 'Hasta $1,000,000 MXN',
            'Media': '$1,000,001 - $2,500,000 MXN',
            'Residencial': 'Más de $2,500,000 MXN',
        }
        rangos_detalle = []
        for nombre in ('Económica', 'Media', 'Residencial'):
            cantidad = conteo_rangos.get(nombre, 0)
            porcentaje = round((cantidad / total) * 100, 1) if total else 0.0
            rangos_detalle.append({
                'nombre': nombre,
                'descripcion': etiquetas_rangos[nombre],
                'cantidad': cantidad,
                'porcentaje': porcentaje,
            })

        estatus_detalle = [
            {
                'clave': 'en_venta',
                'nombre': 'En venta',
                'cantidad': estatus['en_venta'],
                'porcentaje': round((estatus['en_venta'] / total) * 100, 1) if total else 0.0,
            },
            {
                'clave': 'vendida',
                'nombre': 'Vendidas',
                'cantidad': estatus['vendida'],
                'porcentaje': round((estatus['vendida'] / total) * 100, 1) if total else 0.0,
            },
        ]

        return {
            'total_casas': total,
            'rangos': dict(conteo_rangos),
            'estatus': estatus,
            'rangos_detalle': rangos_detalle,
            'estatus_detalle': estatus_detalle,
            'chart_rangos': {
                'labels': [item['nombre'] for item in rangos_detalle],
                'values': [item['cantidad'] for item in rangos_detalle],
            },
            'chart_estatus': {
                'labels': ['En venta', 'Vendidas'],
                'values': [estatus['en_venta'], estatus['vendida']],
            },
        }

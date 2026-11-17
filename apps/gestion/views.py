from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.casas.forms import CasaGestionForm, ImagenGestionForm
from apps.casas.models import Casa, Imagen
from apps.contacto.forms import MensajeContactoGestionForm
from apps.contacto.models import MensajeContacto

from .mixins import StaffPermissionRequiredMixin


class GestionListView(StaffPermissionRequiredMixin, ListView):
    template_name = 'gestion/list.html'
    paginate_by = 25
    fields = ()
    search_fields = ()
    page_title = ''
    list_url_name = ''
    create_url_name = ''
    update_url_name = ''
    delete_url_name = ''

    def get_queryset(self):
        queryset = super().get_queryset()
        if not queryset.ordered:
            queryset = queryset.order_by('-pk')
        search = self.request.GET.get('q', '').strip()
        if search:
            search_query = Q()
            for field in self.search_fields:
                search_query |= Q(**{f'{field}__icontains': search})
            queryset = queryset.filter(search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['list_url_name'] = self.list_url_name
        context['create_url_name'] = self.create_url_name
        context['update_url_name'] = self.update_url_name
        context['delete_url_name'] = self.delete_url_name
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        context['can_add'] = self.request.user.has_perm(f'{app_label}.add_{model_name}')
        context['can_change'] = self.request.user.has_perm(f'{app_label}.change_{model_name}')
        context['can_delete'] = self.request.user.has_perm(f'{app_label}.delete_{model_name}')
        context['columns'] = [label for label, _ in self.fields]
        context['rows'] = [
            {
                'object': obj,
                'values': [self.get_display_value(obj, field) for _, field in self.fields],
            }
            for obj in context['object_list']
        ]
        return context

    @staticmethod
    def get_display_value(obj, field):
        display_method = getattr(obj, f'get_{field}_display', None)
        if display_method:
            return display_method()
        value = getattr(obj, field)
        if isinstance(value, bool):
            return 'Sí' if value else 'No'
        return str(value)


class GestionFormContextMixin:
    page_title = ''
    list_url_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['list_url_name'] = self.list_url_name
        return context

    def get_success_url(self):
        return reverse(self.list_url_name)


class CasaListView(GestionListView):
    model = Casa
    permission_required = 'casas.view_casa'
    page_title = 'Casas'
    list_url_name = 'gestion:casas'
    fields = (
        ('Título', 'titulo'),
        ('Ciudad', 'ciudad'),
        ('Zona', 'zona'),
        ('Precio', 'precio'),
        ('Estatus', 'estatus'),
    )
    search_fields = ('titulo', 'ciudad', 'zona', 'direccion')
    create_url_name = 'gestion:casa_crear'
    update_url_name = 'gestion:casa_editar'
    delete_url_name = 'gestion:casa_eliminar'

class ImagenListView(GestionListView):
    model = Imagen
    permission_required = 'casas.view_imagen'
    page_title = 'Imágenes'
    list_url_name = 'gestion:imagenes'
    fields = (
        ('Casa', 'casa'),
        ('Archivo', 'ruta_imagen'),
        ('Principal', 'es_principal'),
    )
    search_fields = ('casa__titulo', 'casa__ciudad', 'ruta_imagen')
    create_url_name = 'gestion:imagen_crear'
    update_url_name = 'gestion:imagen_editar'
    delete_url_name = 'gestion:imagen_eliminar'

class MensajeContactoListView(GestionListView):
    model = MensajeContacto
    permission_required = 'contacto.view_mensajecontacto'
    page_title = 'Mensajes de contacto'
    list_url_name = 'gestion:mensajes'
    fields = (
        ('Nombre', 'nombre'),
        ('Correo', 'correo'),
        ('Teléfono', 'telefono'),
        ('Fecha', 'fecha_envio'),
    )
    search_fields = ('nombre', 'correo', 'telefono', 'mensaje')
    create_url_name = 'gestion:mensaje_crear'
    update_url_name = 'gestion:mensaje_editar'
    delete_url_name = 'gestion:mensaje_eliminar'


class CasaCreateView(StaffPermissionRequiredMixin, GestionFormContextMixin, CreateView):
    model = Casa
    form_class = CasaGestionForm
    template_name = 'gestion/form.html'
    permission_required = 'casas.add_casa'
    page_title = 'Agregar casa'
    list_url_name = 'gestion:casas'


class CasaUpdateView(StaffPermissionRequiredMixin, GestionFormContextMixin, UpdateView):
    model = Casa
    form_class = CasaGestionForm
    template_name = 'gestion/form.html'
    permission_required = 'casas.change_casa'
    page_title = 'Editar casa'
    list_url_name = 'gestion:casas'


class CasaDeleteView(StaffPermissionRequiredMixin, DeleteView):
    model = Casa
    template_name = 'gestion/confirm_delete.html'
    permission_required = 'casas.delete_casa'
    success_url = reverse_lazy('gestion:casas')
    page_title = 'Eliminar casa'
    list_url_name = 'gestion:casas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['list_url_name'] = self.list_url_name
        return context


class ImagenCreateView(StaffPermissionRequiredMixin, GestionFormContextMixin, CreateView):
    model = Imagen
    form_class = ImagenGestionForm
    template_name = 'gestion/form.html'
    permission_required = 'casas.add_imagen'
    page_title = 'Agregar imagen'
    list_url_name = 'gestion:imagenes'


class ImagenUpdateView(StaffPermissionRequiredMixin, GestionFormContextMixin, UpdateView):
    model = Imagen
    form_class = ImagenGestionForm
    template_name = 'gestion/form.html'
    permission_required = 'casas.change_imagen'
    page_title = 'Editar imagen'
    list_url_name = 'gestion:imagenes'


class ImagenDeleteView(StaffPermissionRequiredMixin, DeleteView):
    model = Imagen
    template_name = 'gestion/confirm_delete.html'
    permission_required = 'casas.delete_imagen'
    success_url = reverse_lazy('gestion:imagenes')
    page_title = 'Eliminar imagen'
    list_url_name = 'gestion:imagenes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['list_url_name'] = self.list_url_name
        return context


class MensajeContactoCreateView(
    StaffPermissionRequiredMixin,
    GestionFormContextMixin,
    CreateView,
):
    model = MensajeContacto
    form_class = MensajeContactoGestionForm
    template_name = 'gestion/form.html'
    permission_required = 'contacto.add_mensajecontacto'
    page_title = 'Agregar mensaje'
    list_url_name = 'gestion:mensajes'


class MensajeContactoUpdateView(
    StaffPermissionRequiredMixin,
    GestionFormContextMixin,
    UpdateView,
):
    model = MensajeContacto
    form_class = MensajeContactoGestionForm
    template_name = 'gestion/form.html'
    permission_required = 'contacto.change_mensajecontacto'
    page_title = 'Editar mensaje'
    list_url_name = 'gestion:mensajes'


class MensajeContactoDeleteView(StaffPermissionRequiredMixin, DeleteView):
    model = MensajeContacto
    template_name = 'gestion/confirm_delete.html'
    permission_required = 'contacto.delete_mensajecontacto'
    success_url = reverse_lazy('gestion:mensajes')
    page_title = 'Eliminar mensaje'
    list_url_name = 'gestion:mensajes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['list_url_name'] = self.list_url_name
        return context

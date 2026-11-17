from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied


class StaffRequiredMixin(LoginRequiredMixin):
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (
            not request.user.is_active or not request.user.is_staff
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class StaffPermissionRequiredMixin(StaffRequiredMixin, PermissionRequiredMixin):
    pass

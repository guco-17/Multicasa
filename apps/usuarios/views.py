from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


class LoginView(auth_views.LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')

    def get_success_url(self):
        if not self.request.user.is_staff:
            return reverse_lazy('home')
        return super().get_success_url()


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('home')

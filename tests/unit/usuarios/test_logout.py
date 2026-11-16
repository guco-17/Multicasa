from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LogoutViewTests(TestCase):
    def test_post_logout_redirects_to_public_home(self):
        user = get_user_model().objects.create_user(
            username='admin-test',
            password='test-password',
        )
        self.client.force_login(user)

        home_response = self.client.get(reverse('home'))
        self.assertContains(home_response, 'method="post"')
        self.assertContains(home_response, 'Cerrar sesión')

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

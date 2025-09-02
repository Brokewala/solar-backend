import time
from django.urls import reverse
from django.test import TestCase
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from users.models import ProfilUser
from users.tasks import send_reset_password_email


class RequestResetPasswordTests(TestCase):
    def setUp(self):
        self.user = ProfilUser.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='John',
            last_name='Doe'
        )
        self.url = reverse('request_reset_password')

    @patch('users.views.send_reset_password_email', side_effect=lambda *args, **kwargs: time.sleep(0.1))
    def test_response_immediate(self, mock_send):
        start = time.time()
        response = self.client.post(self.url, {'email': self.user.email})
        duration = time.time() - start
        self.assertLess(duration, 0.5)
        self.assertEqual(response.status_code, 202)
        mock_send.assert_called_once()

    @patch('users.views.send_reset_password_email')
    def test_user_absent_same_response(self, mock_send):
        response = self.client.post(self.url, {'email': 'absent@example.com'})
        self.assertEqual(response.status_code, 202)
        mock_send.assert_not_called()

    @patch('users.views.send_reset_password_email')
    def test_uid_token_and_link_generated(self, mock_send):
        response = self.client.post(self.url, {'email': self.user.email})
        self.assertEqual(response.status_code, 202)
        email, reset_link, request_id = mock_send.call_args.args
        self.assertEqual(email, self.user.email)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)
        self.assertIn(uidb64, reset_link)
        self.assertIn(token, reset_link)

class SendResetPasswordEmailTests(TestCase):
    @patch('users.tasks.Util.send_email')
    def test_email_sent(self, mock_send):
        send_reset_password_email('task@example.com', 'http://test', request_id='req')
        mock_send.assert_called_once()

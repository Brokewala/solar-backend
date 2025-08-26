import smtplib
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

    @patch('users.views.transaction.on_commit', side_effect=lambda fn: fn())
    @patch('users.views.send_reset_password_email.delay')
    def test_response_immediate(self, mock_delay, mock_on_commit):
        mock_delay.side_effect = lambda *args, **kwargs: time.sleep(0.1)
        start = time.time()
        response = self.client.post(self.url, {'email': self.user.email})
        duration = time.time() - start
        self.assertLess(duration, 0.5)
        self.assertEqual(response.status_code, 202)
        mock_delay.assert_called_once()

    @patch('users.views.transaction.on_commit', side_effect=lambda fn: fn())
    @patch('users.views.send_reset_password_email.delay')
    def test_user_absent_same_response(self, mock_delay, mock_on_commit):
        response = self.client.post(self.url, {'email': 'absent@example.com'})
        self.assertEqual(response.status_code, 202)
        mock_delay.assert_not_called()

    @patch('users.views.transaction.on_commit', side_effect=lambda fn: fn())
    @patch('users.views.send_reset_password_email.delay')
    def test_uid_token_and_link_generated(self, mock_delay, mock_on_commit):
        response = self.client.post(self.url, {'email': self.user.email})
        self.assertEqual(response.status_code, 202)
        user_id, reset_link, request_id = mock_delay.call_args.args
        self.assertEqual(str(user_id), str(self.user.id))
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = PasswordResetTokenGenerator().make_token(self.user)
        self.assertIn(uidb64, reset_link)
        self.assertIn(token, reset_link)


class SendResetPasswordEmailTaskTests(TestCase):
    def setUp(self):
        self.user = ProfilUser.objects.create_user(
            email='task@example.com',
            password='password123',
            first_name='Task',
            last_name='User'
        )

    @patch('users.tasks.logger')
    @patch('users.tasks.EmailMultiAlternatives.send', side_effect=smtplib.SMTPException('boom'))
    def test_retry_on_smtp_error(self, mock_send, mock_logger):
        with self.assertRaises(Exception):
            send_reset_password_email.run(user_id=self.user.id, reset_link='http://test', request_id='req')

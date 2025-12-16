from django.test import TestCase
from users.models import ProfilUser
from notification.models import Notification
from notification.services import create_or_replace_notification

class NotificationDeduplicationTest(TestCase):
    def setUp(self):
        self.user = ProfilUser.objects.create(
            username="testuser", 
            email="test@example.com",
            password="password"
        )

    def test_deduplication(self):
        # 1. Create first notification
        notif1 = create_or_replace_notification(self.user.id, "TestFunc", "Hello World")
        self.assertEqual(Notification.objects.count(), 1)
        
        # 2. Create identical notification
        notif2 = create_or_replace_notification(self.user.id, "TestFunc", "Hello World")
        
        # Should still be 1 total, but a NEW object ID (replaced)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertNotEqual(notif1['id'], notif2['id'])
        
        # 3. Create different message
        create_or_replace_notification(self.user.id, "TestFunc", "Different Message")
        self.assertEqual(Notification.objects.count(), 2)

    def test_deduplication_different_function(self):
        create_or_replace_notification(self.user.id, "FuncA", "Message")
        create_or_replace_notification(self.user.id, "FuncB", "Message")
        self.assertEqual(Notification.objects.count(), 2)

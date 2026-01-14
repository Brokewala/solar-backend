from django.test import TestCase
from users.models import ProfilUser
from notification.models import Notification
from notification.services import create_or_replace_notification

class NotificationDeduplicationTest(TestCase):
    def setUp(self):
        self.user = ProfilUser.objects.create(
            email="test@example.com",
            password="password"
        )

    def test_deduplication_last_3(self):
        # 1. Create 3 different notifications
        create_or_replace_notification(self.user.id, "TestFunc", "Message 1")
        create_or_replace_notification(self.user.id, "TestFunc", "Message 2")
        create_or_replace_notification(self.user.id, "TestFunc", "Message 3")
        self.assertEqual(Notification.objects.count(), 3)
        
        # 2. Create a duplicate of one of the last 3 (Message 2)
        result = create_or_replace_notification(self.user.id, "TestFunc", "Message 2")
        # Should be ignored (return None)
        self.assertIsNone(result)
        self.assertEqual(Notification.objects.count(), 3)
        
        # 3. Create a new unique notification
        create_or_replace_notification(self.user.id, "TestFunc", "Message 4")
        self.assertEqual(Notification.objects.count(), 4)
        
        # 4. Create a duplicate of "Message 1" (which is now the 4th oldest, so NOT in last 3)
        # Last 3 are: Message 4, Message 3, Message 2.
        # Message 1 is outside the window.
        result = create_or_replace_notification(self.user.id, "TestFunc", "Message 1")
        # Should be created
        self.assertIsNotNone(result)
        self.assertEqual(Notification.objects.count(), 5)

    def test_deduplication_different_function(self):
        create_or_replace_notification(self.user.id, "FuncA", "Message")
        create_or_replace_notification(self.user.id, "FuncB", "Message")
        self.assertEqual(Notification.objects.count(), 2)

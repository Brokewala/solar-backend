import logging
from django.db import transaction
from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)

def create_or_replace_notification(user_id, fonction, message):
    """
    Creates a new notification for the user.
    If a notification with the exact same 'fonction' and 'message' already exists for this user,
    it removes the old one(s) and creates a fresh one (effectively updating the timestamp).
    Ensures that only ONE notification of this specific type/content exists for the user.
    """
    if not user_id:
        return None

    try:
        with transaction.atomic():
            # 1. Search for existing duplicates based on business key (user + fonction + message)
            existing_notifs = Notification.objects.filter(
                user_id=user_id,
                fonction=fonction,
                message=message
            )
            
            if existing_notifs.exists():
                count = existing_notifs.count()
                logger.info(f"Removing {count} duplicate notification(s) for user {user_id} - {fonction}")
                existing_notifs.delete()

            # 2. Create the new notification
            notif = Notification.objects.create(
                user_id=user_id,
                fonction=fonction,
                message=message,
            )
            
            # Return serialized data directly as it's often what's needed for sockets
            return NotificationSerializer(notif, many=False).data
            
    except Exception as e:
        logger.error(f"Error in create_or_replace_notification: {e}")
        return None

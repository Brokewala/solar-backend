import logging
from django.db import transaction
from .models import Notification
from .serializers import NotificationSerializer

logger = logging.getLogger(__name__)

def create_or_replace_notification(user_id, fonction, message):
    """
    Creates a new notification for the user ONLY if the message is different
    from the last 3 notifications for the same 'fonction'.
    """
    if not user_id:
        return None

    try:
        with transaction.atomic():
            # 1. Get the last 3 notifications for this user and function
            last_notifs = Notification.objects.filter(
                user_id=user_id,
                fonction=fonction
            ).order_by('-createdAt')[:3]

            # 2. Check if the new message exists in these last 3
            # We compare the 'message' field.
            for notif in last_notifs:
                if notif.message == message:
                    # Found a duplicate in the last 3 -> Ignore creation
                    logger.info(f"Duplicate notification ignored for user {user_id} - {fonction}: {message}")
                    return None

            # 3. Create the new notification if no duplicate found
            new_notif = Notification.objects.create(
                user_id=user_id,
                fonction=fonction,
                message=message,
            )
            
            # Return serialized data directly
            return NotificationSerializer(new_notif, many=False).data
            
    except Exception as e:
        logger.error(f"Error in create_or_replace_notification: {e}")
        return None

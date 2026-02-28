from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Notification


def send_notification(user, message):
    channel_layer = get_channel_layer()

    # Save to DB
    Notification.objects.create(
        organization=user.organization,
        recipient=user,
        message=message
    )

    # Send real-time event
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "message": message
        }
    )
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





from django.core.mail import send_mail
from django.conf import settings


def send_system_email(subject, message, recipient_list):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
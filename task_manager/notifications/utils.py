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




from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site

def send_Project_creation_email(user, project):
    subject = "New Project Created"

    message = f"""
Hello {user.username},
A New Project {project.name} Has been created by {project.created_by.username}

Best regards,
{project.organization.name} Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )






def send_Project_completion_email(user, project):
    subject = "Project Completion"

    message = f"""
    Hello {user.username},
    {project.name} Has been completed.

    Best regards,
    {project.organization.name} Team
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
	





def send_task_assignment_email(user, task):
    subject = "New task Alert"

    message = f"""
    Hello {user.username},
    You have been assigned to perfom Task {task.title} part of {task.project.name} Project.

    Best regards,
    {task.project.organization.name} Team
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
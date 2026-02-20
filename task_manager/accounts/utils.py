from django.core.mail import send_mail
from django.conf import settings

def send_temporary_password_email(user, temp_password):
    subject = "Your Account Has Been Created"

    message = f"""
Hello {user.username},

An account has been created for you.

Temporary Password: {temp_password}

Please login and change your password immediately.

Best regards,
Your Organization Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

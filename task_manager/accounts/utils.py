from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import email_verification_token


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


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    verification_url = f"{request.scheme}://{request.get_host()}/api/auth/verify-email/{uid}/{token}/"

    subject = "Verify Your Email"

    message = f"""
Hi {user.username},

Please verify your email by clicking the link below:

{verification_url}

Thank you.
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
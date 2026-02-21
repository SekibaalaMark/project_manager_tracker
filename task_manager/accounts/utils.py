from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site

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



from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import email_verification_token

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    #link = reverse('register', kwargs={'uidb64': uid, 'token': token})
    #verification_url = f"{request.scheme}://{request.get_host()}{link}"

    verification_url = f"http://127.0.0.1:8000/api/auth/verify-email/{uid}/{token}/"
    #current_site = Site.objects.get_current()
    #domain = current_site.domain  # e.g., 'myapp.com'
    #verification_url = f"https://{domain}/api/auth/verify-email/{uid}/{token}/"

    subject = "Verify Your Email"
    text_content = f"""
Hi {user.username},

Please verify your email by clicking the link below:

{verification_url}
"""

    html_content = f"""
    <h2>Email Verification</h2>
    <p>Hi {user.username},</p>
    <p>Please click the link below to verify your email:</p>
    <a href="{verification_url}">Verify Email</a>
    """

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
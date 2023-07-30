from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_email(email, token_id, user_id):
    subject = "Account Verification"
    activation_link = f"{settings.ACTIVATION_LINK}{token_id}&user_id={user_id}"
    message = f"Click the link below to verify your email address:\n\n{activation_link}"
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email=from_email, recipient_list=[email])

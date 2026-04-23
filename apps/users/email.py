from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

def send_account_setup_email(user, request):
    token = signing.dumps(user.pk, salt="account-setup")
    setup_url = request.build_absolute_uri(
        reverse("users:account_setup", kwargs={"token": token})
    )
    send_mail(
        subject="Your Procurement System Account",
        message=f"""
Hi {user.full_name},

An account has been created for you in the WMSU Procurement System.

Please complete your account setup by clicking the link below.
This linke will expire in 24 hours.

{setup_url}

If you did not expect this email, please ignore it.
        """,
        from_email="noreply@wmsu.edu.ph",
        recipient_list=[user.email],
        fail_silently=False,
    )
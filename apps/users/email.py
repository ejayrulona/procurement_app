from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

def send_account_setup_email(user, request):
    token = signing.dumps(user.pk, salt="account-setup")
    setup_url = request.build_absolute_uri(
        reverse("users:setup_account", kwargs={"token": token})
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
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_account_activated_email(user, request):
    login_url = request.build_absolute_uri(reverse("core:home"))
    send_mail(
        subject="",
        message=f"""
Hi {user.full_name},

Your account in the WSMU Procurement Office has been activated.
You may now log in to the system using the link below:

{login_url}

If you did not expect this change or believe this was an error,
please contact the procurement office immediately.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )

def send_account_deactivated_email(user):
    send_mail(
        subject="",
        message=f"""
Hi {user.full_name},

Your account in the WSMU Procurement Office has been deactivated.
You will not be able to log in until your account is reactivated.

If you believe this was done in error, please contact the procurement office immediately.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )

def send_registration_confirmation_email(user, request):
    status_url = request.build_absolute_uri(
        reverse("users:college_account_status", kwargs={"username": user.username})
    )
    send_mail(
        subject="Registration Request Recieved",
        message=f"""
Hi {user.full_name},

Your registration request for the WMSU Procurement System has been received
and is currently pending review.

You can check your registration status anytime using the below:

{status_url}

You will be notified via email once your request has been reviewed.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_registration_approved_email(user, request):
    login_url = request.build_absolute_uri(reverse("core:home"))
    send_mail(
        subject="Registration Approved - You Can Now Log In",
        message=f"""
Hi {user.full_name},

Your registration request for WMSU University Procurement System has been approved.

You may now log in to the system using the link below:

{login_url}
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_registration_declined_email(user, remarks):
    send_mail(
        subject="Registration Request Declined",
        message=f"""
Hi {user.full_name},

Unfortunately your registration request for the University Procurement System
has been declined.

{"Reason: " + remarks if remarks else "No reason was provided."}

If you believe this a mistake, please contact the procurement office directly.
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
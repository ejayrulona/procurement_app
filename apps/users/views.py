from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .decorators import admin_required, any_admin_required
from .email import (
    send_account_setup_email, send_account_activated_email,
    send_account_deactivated_email, send_email_verification, 
    send_registration_approved_email, send_registration_declined_email
)
from .forms import (
    UserForm, UserEditForm, ChangePasswordForm, AdminProfileForm,OfficeReapplyUserForm, 
    OfficeProfileForm, AdminAidCreationForm, AdminAidSetupForm, AdminAidSetupProfileForm
)
from .models import (
    User, AdminProfile, OfficeProfile, RegistrationRequest, AccountSetupToken, 
    EmailVerificationToken
)

@admin_required
def create_admin_aid(request):
    if request.method == "POST":
        form = AdminAidCreationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=f"pending_{form.cleaned_data['email'].split('@')[0]}",
                    password=None,
                    first_name=form.cleaned_data["first_name"],
                    middle_name=form.cleaned_data.get("middle_name", ""),
                    last_name=form.cleaned_data["last_name"],
                    email=form.cleaned_data["email"],
                    phone_number=form.cleaned_data.get("phone_number", ""),
                    role=User.Role.ADMIN_AID,
                    email_verified=False,
                    is_active=False,
                )

                AdminProfile.objects.create(
                    user=user,
                    employee_id_number=form.cleaned_data["employee_id_number"],
                    is_setup_complete=False,
                )

                send_account_setup_email(user, request)

            messages.success(request, f"Account created and setup email sent to {user.email}.")
            return redirect("users:list_admin_aid_accounts")
    else:
        form = AdminAidCreationForm()

    context = {
        "form": form
    }
    return render(request, "users/create_admin_aid.html", context)


@admin_required
def list_admin_aid_accounts(request):
    aid_accounts = User.objects.filter(
        role=User.Role.ADMIN_AID
    ).select_related(
        "admin_profile"
    ).order_by("-date_joined")

    total_count = aid_accounts.count()
    active_count = aid_accounts.filter(is_active=True).count()
    inactive_count = aid_accounts.filter(is_active=False, admin_profile__is_setup_complete=True).count()
    pending_setup_count = aid_accounts.filter(admin_profile__is_setup_complete=False).count()

    context = {
        "aid_accounts": aid_accounts,
        "total_count": total_count,
        "active_count": active_count,
        "inactive_count": inactive_count,
        "pending_setup_count": pending_setup_count
    }

    return render(request, "users/admin_aid_accounts.html", context)


def setup_account(request, token):
    # Validate the token
    try:
        user_pk = signing.loads(token, salt="account-setup", max_age=86400)
    except signing.SignatureExpired:
        messages.error(request, "This setup link has expired. Please contact the admin for a new one.")
        return redirect("core:home")
    except signing.BadSignature:
        messages.error(request, "This setup link is invalid.")
        return redirect("core:home")
    
    # Verify if the setup is not already complete
    user = get_object_or_404(User, pk=user_pk)
    profile = get_object_or_404(AdminProfile, user=user)

    if profile.is_setup_complete:
        messages.info(request, "Your account has already been set up. Please log in.")
        return redirect("core:home")
    
    # Verify if the token exists in the database
    stored_token = AccountSetupToken.objects.filter(user=user, token=token).first()
    if not stored_token:
        messages.error(request, "This setup link has already been superseded. Please use the latest email")
        return redirect("core:home")
    
    if stored_token.is_expired:
        messages.error(request, "This verification link has expired. Please request a new one.")
        return redirect("core:home")
    
    if request.method == "POST":
        setup_form = AdminAidSetupForm(request.POST, instance=user)
        admin_aid_profile_form = AdminAidSetupProfileForm(request.POST, request.FILES, instance=profile)

        if setup_form.is_valid() and admin_aid_profile_form.is_valid():
            with transaction.atomic():
                user = setup_form.save(commit=False)
                user.set_password(setup_form.cleaned_data["password1"])
                user.email_verified = True
                user.is_active = True
                user.save()

                profile = admin_aid_profile_form.save(commit=False)
                profile.is_setup_complete = True
                profile.save()

                stored_token.delete()

            messages.success(request, "Your account setup is complete. You may now log in.")
            return redirect("core:home")
    else:
        setup_form = AdminAidSetupForm(instance=user)
        admin_aid_profile_form = AdminAidSetupProfileForm(instance=profile)

    context = {
        "setup_form": setup_form,
        "admin_aid_profile_form": admin_aid_profile_form,
        "user": user,
    }

    return render(request, "users/aid_account_confirmation.html", context)


@admin_required
def resend_setup_email(request, id):
    user = get_object_or_404(User, pk=id, role=User.Role.ADMIN_AID)

    if user.admin_profile.is_setup_complete:
        messages.info(request, "This account has already been set up.")
        return redirect("users:list_admin_aid_accounts")
    
    send_account_setup_email(user, request)
    messages.success(request, f"Setup email resent to {user.email}.")

    return redirect("users:list_admin_aid_accounts")


@admin_required
def toggle_user_status(request, id):
    user = get_object_or_404(User, pk=id, role=User.Role.ADMIN_AID)

    if not user.admin_profile.is_setup_complete:
        messages.error(request, "Cannot change status of an account that has not completed setup.")
        return redirect("users:list_admin_aid_accounts")
    
    if request.method == "POST":
        user.is_active = not user.is_active
        user.save()

        if user.is_active:
            send_account_activated_email(user, request)
        else:
            send_account_deactivated_email(user)
        
        status_label = "activated" if user.is_active else "deactivated"
        messages.success(request, f"{user.full_name} has been {status_label}.")

    return redirect("users:list_admin_aid_accounts")


def office_register(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, prefix="user")
        office_profile_form = OfficeProfileForm(request.POST, prefix="office_profile")

        if user_form.is_valid() and office_profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.role = User.Role.OFFICE
                user.is_active = False
                user.save()

                office_profile = office_profile_form.save(commit=False)
                office_profile.user = user
                office_profile.save()

                RegistrationRequest.objects.create(user=user)
                send_email_verification(user, request)

            messages.success(request, "Registration request sent. Check your email to verify your account.")
            return redirect("core:home", username=user.username)
    else:
        user_form = UserForm(prefix="user")
        office_profile_form = OfficeProfileForm(prefix="office_profile")

    context = {
        "user_form": user_form,
        "office_profile_form": office_profile_form,
    }

    return render(request, "users/office_registration.html", context)


def verify_email(request, token):
    # Validate token signature and expiry
    try:
        user_pk = signing.loads(token, salt="email-verification", max_age=86400)
    except signing.SignatureExpired:
        messages.error(request, "This verification link has expired. Please request a new one.")
        return redirect("users:resend_verification", )
    except signing.BadSignature:
        messages.error(request, "This verification link is invalid.")
        return redirect("users:login")

    user = get_object_or_404(User, pk=user_pk)

    if user.email_verified:
        messages.info(request, "Your email is already verified.")
        return redirect("users:office_account_status", username=user.username)

    # Check token exists in database
    stored_token = EmailVerificationToken.objects.filter(
        user=user, token=token
    ).first()

    if not stored_token:
        messages.error(request, "This verification link has already been used or superseded.")
        return redirect("users:login")

    if stored_token.is_expired:
        messages.error(request, "This verification link has expired. Please request a new one.")
        return redirect("users:office_account_status", username=user.username)

    with transaction.atomic():
        user.email_verified = True
        user.save()
        stored_token.delete()

    messages.success(request, "Your email has been verified successfully.")
    return redirect("users:office_account_status", username=user.username)


def resend_verification_email(request, username):
    user = get_object_or_404(User, username=username)

    if user.email_verified:
        messages.info(request, "Your email is already verified.")
        return redirect("users:office_account_status", username=username)

    send_email_verification(user, request)
    messages.success(request, "A new verification email has been sent.")
    return redirect("users:office_account_status", username=username)


def office_account_status(request, username):
    user = get_object_or_404(User, username=username, role=User.Role.OFFICE)
    registration_request = RegistrationRequest.objects.filter(user=user, is_latest=True).first()

    if not registration_request:
        return redirect("users:office_register")
    
    context = {
        "user": user,
        "registration_request": registration_request,
        "email_verified": user.email_verified,
    }

    return render(request, "users/office_account_status.html", context)


@any_admin_required
def list_registration_requests(request):
    account_requests = RegistrationRequest.objects.filter(
        user__role=User.Role.OFFICE,
        is_latest=True,
    ).select_related(
        "user",
        "user__office_profile",
        "reviewed_by",
    ).order_by("-created_at")
    
    pending_count = account_requests.filter(status=RegistrationRequest.Status.PENDING).count()
    declined_count = account_requests.filter(status=RegistrationRequest.Status.DECLINED).count()
    approved_count = account_requests.filter(status=RegistrationRequest.Status.APPROVED).count()

    context = {
        "account_requests": account_requests,
        "pending_count": pending_count,
        "declined_count": declined_count,
        "approved_count": approved_count,
    }
    
    return render(request, "users/registration_requests.html", context)


@any_admin_required
def approve_registration_request(request, id):
    user = get_object_or_404(User, pk=id, role=User.Role.OFFICE)
    registration_request = RegistrationRequest.objects.filter(
        user=user, is_latest=True
    ).first()

    if not registration_request:
        messages.error(request, "No registration request found.")
        return redirect("users:list_registration_requests")

    if registration_request.status != RegistrationRequest.Status.PENDING:
        messages.error(request, "This request has already been reviewed.")
        return redirect("users:list_registration_requests")
    
    with transaction.atomic():
        registration_request.status = RegistrationRequest.Status.APPROVED
        registration_request.reviewed_by = request.user
        registration_request.reviewed_at = timezone.now()
        registration_request.save()

        registration_request.user.is_active = True
        registration_request.user.save()

    send_registration_approved_email(registration_request.user, request)
    messages.success(request, f"{registration_request.user.full_name}'s registration has been approved.")
    return redirect("users:list_registration_requests")


@any_admin_required
def decline_registration_request(request, id):
    user = get_object_or_404(User, pk=id, role=User.Role.OFFICE)
    registration_request = RegistrationRequest.objects.filter(
        user=user, is_latest=True
    ).first()

    if not registration_request:
        messages.error(request, "No registration request found.")
        return redirect("users:list_registration_requests")

    if registration_request.status != RegistrationRequest.Status.PENDING:
        messages.error(request, "This request has already been reviewed.")
        return redirect("users:list_registration_requests")
    
    remarks = request.POST.get("remarks", "").strip()
    
    with transaction.atomic():
        registration_request.status = RegistrationRequest.Status.DECLINED
        registration_request.reviewed_by = request.user
        registration_request.reviewed_at = timezone.now()
        registration_request.remarks = remarks
        registration_request.save()

    send_registration_declined_email(registration_request.user, remarks)
    messages.success(request, f"{registration_request.user.full_name}'s registration has been declined.")
    return redirect("users:list_registration_requests")

def reapply_registration(request, username):
    user = get_object_or_404(User, username=username, role=User.Role.OFFICE,)
    office_profile = get_object_or_404(OfficeProfile, user=user)
    latest_request = RegistrationRequest.objects.filter(
        user=user, is_latest=True
    ).first()

    if not latest_request or latest_request.status != RegistrationRequest.Status.DECLINED:
        messages.error(request, "Only declined applications can be reapplied.")
        return redirect("users:office_account_status", username=username)
    
    if request.method == "POST":
        user_form = OfficeReapplyUserForm(request.POST, instance=user, prefix="user")
        office_profile_form = OfficeProfileForm(request.POST, instance=office_profile, prefix="office_profile")

        if user_form.is_valid() and office_profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                office_profile_form.save()

                latest_request.is_latest = False
                latest_request.save()

                new_request = RegistrationRequest.objects.create(
                    user=user,
                    is_latest=True,
                    status=RegistrationRequest.Status.PENDING,
                )

                user.is_active = False
                user.save()

                send_email_verification(user, request)

            return redirect("users:office_account_status", username=username)
        
    else:
        user_form = OfficeReapplyUserForm(instance=user, prefix="user")
        office_profile_form = OfficeProfileForm(instance=office_profile, prefix="office_profile")

    context = {
        "user": user,
        "user_form": user_form,
        "office_profile_form": office_profile_form,
        "is_reapply": True,
    }

    return render(request, "users/office_registration.html", context)


@login_required
def profile(request, id):
    user = get_object_or_404(User, pk=id)
    user_profile = (
        get_object_or_404(AdminProfile, user=user)  
        if user.role in (User.Role.ADMIN, User.Role.ADMIN_AID)
        else get_object_or_404(OfficeProfile, user=user)
    )

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=user, prefix="user")
        user_profile_form = (
            AdminProfileForm(request.POST, request.FILES, instance=user_profile, prefix="admin_profile")
            if user.role in (User.Role.ADMIN, User.Role.ADMIN_AID)
            else OfficeProfileForm(request.POST, instance=user_profile, prefix="office_profile")
        )

        if user_form.is_valid() and user_profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                user_profile_form.save()

            messages.success(request, "Your profile has been updated.")
            return redirect("users:profile", id=id)
    else:
        user_form = UserEditForm(instance=user, prefix="user")
        user_profile_form = (
            AdminProfileForm(instance=user_profile, prefix="admin_profile")
            if user.role in (User.Role.ADMIN, User.Role.ADMIN_AID)
            else OfficeProfileForm(instance=user_profile, prefix="office_profile")
        )

    context = {
        "user": user,
        "user_form": user_form,
        "user_profile_form": user_profile_form,
    }

    return render(request, "users/profile.html", context)


@login_required
def settings(request):
    return render(request, "users/settings.html")


def change_password(request, id):
    user = get_object_or_404(User, pk=id)

    if request.method == "POST":
        form = ChangePasswordForm(data=request.POST, user=user)

        if form.is_valid():
            form.save()

            messages.success(request, "Password has been changed successfully.")
            return redirect("users:settings")
        
    else:
        form = ChangePasswordForm(user=user)

    context = {
        "form": form,
    }

    return render(request, "users/change-password.html", context)


def forgot_password(request):
    return render(request, "users/forgot-password.html")

def account_verification(request):
    return render(request, "users/account-verification.html")

def email_sent(request):
    return render(request, "users/email-sent.html")
from django.contrib import messages
from django.core import signing
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .email import (
    send_account_setup_email, send_registration_confirmation_email, 
    send_registration_approved_email, send_registration_declined_email
)
from .forms import (
    UserForm, AdminProfileForm, CollegeReapplyUserForm, CollegeProfileForm, 
    AdminAidCreationForm, AdminAidSetupForm, AdminAidSetupProfileForm
)
from .models import CollegeOffice, User, AdminProfile, CollegeProfile, RegistrationRequest

def create_admin_aid(request):
    if request.method == "POST":
        form = AdminAidCreationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=f"pending_{form.cleaned_data['email'].split('@'[0])}",
                    password=None,
                    first_name=form.cleaned_data["first_name"],
                    middle_name=form.cleaned_data.get("middle_name", ""),
                    last_name=form.cleaned_data["last_name"],
                    email=form.cleaned_data["email"],
                    phone_number=form.cleaned_data.get("phone_number", ""),
                    role=User.Role.ADMIN_AID,
                    is_active=False,
                )

                AdminProfile.objects.create(
                    user=user,
                    employee_id_number=form.cleaned_data["employee_id_number"],
                    is_setup_complete=False,
                )

                send_account_setup_email(user, request)
                messages.success(request, f"Account created and setup email sent to {user.email}.")
                return redirect("core:home")    # Change to admin_aid_list
    else:
        form = AdminAidCreationForm(prefix="admin_profile")

    context = {
        "form": form
    }
    return render(request, "users/create_admin_aid.html", context)

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
    
    if request.method == "POST":
        setup_form = AdminAidSetupForm(request.POST, instance=user)
        admin_aid_profile_form = AdminAidSetupProfileForm(request.POST, request.FILES, instance=profile)

        if setup_form.is_valid() and admin_aid_profile_form.is_valid():
            with transaction.atomic():
                user = setup_form.save(commit=False)
                user.set_password(setup_form.cleaned_data["password1"])
                user.is_active = False
                user.save()

                profile = admin_aid_profile_form.save(commit=False)
                profile.is_setup_complete = True
                profile.save()

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

def resend_setup_email(request, id):
    user = get_object_or_404(User, pk=id, role=User.Role.ADMIN_AID)
    admin_profile = get_object_or_404(AdminProfile, user=user)

    if admin_profile.is_setup_complete:
        messages.info(request, "This account has already been set up.")
        return redirect("users:admin_aid_list")
    
    send_account_setup_email(user, request)
    messages.success(request, f"Setup email resent to {user.email}.")

    return redirect("users:admin_aid_list")

def register_college(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, prefix="user")
        college_profile_form = CollegeProfileForm(request.POST, prefix="college_profile")

        if user_form.is_valid() and college_profile_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.role = User.Role.COLLEGE
                user.is_active = False
                user.save()

                college_profile = college_profile_form.save(commit=False)
                college_profile.user = user
                college_profile.save()

                RegistrationRequest.objects.create(user=user)
                send_registration_confirmation_email(user, request)

                return redirect("users:college_account_status", username=user.username)
    else:
        user_form = UserForm(prefix="user")
        college_profile_form = CollegeProfileForm(prefix="college_profile")

    context = {
        "user_form": user_form,
        "college_profile_form": college_profile_form,
        "colleges_offices": CollegeOffice.objects.all()
    }

    return render(request, "users/college_registration.html", context)

def college_account_status(request, username):
    user = get_object_or_404(User, username=username, role=User.Role.COLLEGE)
    registration_request = RegistrationRequest.objects.filter(user=user, is_latest=True).first()

    if not registration_request:
        return redirect("users:register_college")
    
    context = {
        "user": user,
        "registration_request": registration_request
    }

    return render(request, "users/college_account_status.html", context)

def list_registration_requests(request):
    account_requests = RegistrationRequest.objects.filter(
        user__role=User.Role.COLLEGE,
        is_latest=True,
    ).select_related(
        "user",
        "user__college_profile",
        "user__college_profile__college_office",
        "reviewed_by",
    ).order_by("-created_at")

    context = {
        "account_requests": account_requests,
    }
    
    return render(request, "users/registration_requests.html", context)

def approve_registration_request(request, id):
    user = get_object_or_404(User, pk=id, role=User.Role.COLLEGE)
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

def decline_registration_request(request, id):
    user = get_object_or_404(User, pk=id, role=User.Role.COLLEGE)
    registration_request = RegistrationRequest.objects.filter(
        user=user, is_latest=True
    ).first()

    if not registration_request:
        messages.error(request, "No registration request found.")
        return redirect("users:list_registration_requests")

    if registration_request.status != RegistrationRequest.Status.PENDING:
        messages.error(request, "This request has already been reviewed.")
        return redirect("users:list_registration_requests")
    
    remarks = request.POST.get("remakrs", "").strip()
    
    with transaction.atomic():
        registration_request.status = RegistrationRequest.Status.APPROVED
        registration_request.reviewed_by = request.user
        registration_request.reviewed_at = timezone.now()
        registration_request.remarks = remarks
        registration_request.save()

    send_registration_declined_email(registration_request.user, remarks)
    messages.success(request, f"{registration_request.user.full_name}'s registration has been declined.")
    return redirect("users:list_registration_requests")

def reapply_registration(request, username):
    user = get_object_or_404(User, username=username, role=User.Role.COLLEGE,)
    college_profile = get_object_or_404(CollegeProfile, user=user)
    latest_request = RegistrationRequest.objects.filter(
        user=user, is_latest=True
    ).first()

    if not latest_request or latest_request.status != RegistrationRequest.Status.DECLINED:
        messages.error(request, "Only declined applications can be reapplied.")
        return redirect("users:college_account_status", username=username)
    
    if request.method == "POST":
        user_form = CollegeReapplyUserForm(request.POST, instance=user, prefix="user")
        college_profile_form = CollegeProfileForm(request.POST, instance=college_profile, prefix="college_profile")

        if user_form.is_valid() and college_profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                college_profile_form.save()

                latest_request.is_latest = False
                latest_request.save()

                new_request = RegistrationRequest.objects.create(
                    user=user,
                    is_latest=True,
                    status=RegistrationRequest.Status.PENDING,
                )

                user.is_active = False
                user.save()

                send_registration_confirmation_email(user, request)

            return redirect("users:college_account_status", username=username)
        
    else:
        user_form = CollegeReapplyUserForm(instance=user, prefix="user")
        college_profile_form = CollegeProfileForm(instance=college_profile, prefix="college_profile")

    context = {
        "user": user,
        "user_form": user_form,
        "college_profile_form": college_profile_form,
        "colleges_offices": CollegeOffice.objects.all(),
        "is_reapply": True,
    }

    return render(request, "users/college_registration.html", context)

def profile(request):
    return render(request, "users/profile.html")

def settings(request):
    return render(request, "users/settings.html")

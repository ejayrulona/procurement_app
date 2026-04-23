from django.contrib import messages
from django.core import signing
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .email import send_account_setup_email
from .forms import UserForm, AdminProfileForm, CollegeProfileForm, AdminAidCreationForm, AdminAidSetupForm, AdminAidSetupProfileForm
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
                return redirect("core:home")    # Change to status/pending page
    else:
        form = AdminAidCreationForm(prefix="admin_profile")

    context = {
        "form": form
    }
    return render(request, "users/admin_registration.html", context)

def account_setup(request, token):
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

    return render(request, "users/account_setup.html", context)

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

                return redirect("core:home")    # Change to status/pending page
    else:
        user_form = UserForm(prefix="user")
        college_profile_form = CollegeProfileForm(prefix="college_profile")

    context = {
        "user_form": user_form,
        "college_profile_form": college_profile_form,
        "colleges_offices": CollegeOffice.objects.all()
    }

    return render(request, "users/college_registration.html", context)

def profile(request):
    return render(request, "users/profile.html")

def settings(request):
    return render(request, "users/settings.html")

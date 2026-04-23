from django.db import transaction
from django.shortcuts import render, redirect
from . models import CollegeOffice, User, AdminProfile, CollegeProfile, RegistrationRequest
from . forms import UserForm, AdminProfileForm, CollegeProfileForm

def register_admin(request):
    if request.method == "POST":
        user_form = UserForm(request.POST, request.FILES, prefix="user")
        admin_profile_form = AdminProfileForm(request.POST, prefix="admin_profile")

        if user_form.is_valid() and admin_profile_form.is_valid():
            user = user_form.save(commit=False)
            user.role = User.Role.ADMIN
            user.is_active = False
            user.save()

            admin_profile = admin_profile_form.save(commit=False)
            admin_profile.user = user
            admin_profile.save()

            RegistrationRequest.objects.create(user=user)
            return redirect("core:home")    # Change to status/pending page
    else:
        user_form = UserForm(prefix="user")
        admin_profile_form = AdminProfileForm(prefix="admin_profile")

    context = {
        "user_form": user_form,
        "admin_profile_form": admin_profile_form
    }
    return render(request, "users/admin_registration.html", context)


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

def admin_registration(request):
    return render(request, "users/admin_registration.html")

def settings(request):
    return render(request, "users/settings.html")

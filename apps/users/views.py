from django.shortcuts import render

def register_user(request):
    return render(request, "users/registration.html")

def profile(request):
    return render(request, "users/profile.html")

def admin_registration(request):
    return render(request, "users/admin_registration.html")

def settings(request):
    return render(request, "users/settings.html")
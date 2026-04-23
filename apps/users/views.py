from django.shortcuts import render

def register(request):
    return render(request, "users/register.html")

def profile(request):
    return render(request, "users/profile.html")

def admin_registration(request):
    return render(request, "users/admin_registration.html")

def settings(request):
    return render(request, "users/settings.html")

def aid_confirmation(request):
    return render(request, "users/aid_confirmation.html")
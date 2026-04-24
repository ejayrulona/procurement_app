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

def status(request):
    return render(request, "users/status.html")

def account_pending(request):
    return render(request, "users/account_pending.html")

def registration_request(request):
    return render(request, "users/registration_request.html")

def registration_request(request):
    return render(request, "users/registration_request.html")
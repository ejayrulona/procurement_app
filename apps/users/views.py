from django.shortcuts import render

def register_user(request):
    return render(request, "users/registration.html")

def profile(request):
    return render(request, "users/profile.html")
from django.urls import path
from . import views

app_name = "users"

urlpatterns = (
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("admin_registration/", views.admin_registration, name="admin_registration"),
    path("settings/", views.settings, name="settings"),
    path("aid_confirmation/", views.aid_confirmation, name="aid_confirmation"),
)
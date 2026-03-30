from django.urls import path
from . import views

app_name = "users"

urlpatterns = (
    path("register/", views.register_user, name="register_user"),
    path("profile/", views.profile, name="profile"),
    path("admin_registration", views.admin_registration, name="admin_registration"),
)
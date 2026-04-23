from django.urls import path
from . import views

app_name = "users"

urlpatterns = (
    path("register_admin", views.register_admin, name="register_admin"),
    path("register_college/", views.register_college, name="register_college"),
    path("profile/", views.profile, name="profile"),
<<<<<<< HEAD
=======
    path("admin_registration", views.admin_registration, name="admin_registration"),
    path("settings/", views.settings, name="settings"),
>>>>>>> 57f5781a1af2ec60483e79846dad01ad89a14f38
)
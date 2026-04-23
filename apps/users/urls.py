from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "users"

urlpatterns = (
    path("logout/", auth_views.LogoutView.as_view(next_page="core:home"), name="logout"),
    path("create-admin-aid/", views.create_admin_aid, name="create-admin-aid"),
    path("account-setup/", views.account_setup, name="account-setup"),
    path("resend-setup-email/<int:id>/", views.resend_setup_email, name="resend-setup-email"),
    path("register-college/", views.register_college, name="register-college"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings, name="settings"),
)
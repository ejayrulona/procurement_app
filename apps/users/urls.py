from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "users"

urlpatterns = (
    path("logout/", auth_views.LogoutView.as_view(next_page="core:home"), name="logout"),
    path("admin-aid/create", views.create_admin_aid, name="create_admin_aid"),
    path("admin-aid/resend-email/<int:id>/", views.resend_setup_email, name="resend_setup_email"),
    path("account/setup/<str:token>", views.setup_account, name="setup_account"),
    path("register/college", views.register_college, name="register_college"),
    path("register/college/status/<str:username>/", views.college_account_status, name="college_account_status"),
    path("register/college/reapply/<str:username>/", views.reapply_registration, name="reapply_registration"),
    path("admin/registration-requests/", views.list_registration_requests, name="list_registration_requests"),
    path("admin/registration-requests/<int:id>/approve", views.approve_registration_request, name="approve_registration_request"),
    path("admin/registration-requests/<int:id>/decline", views.decline_registration_request, name="decline_registration_request"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings, name="settings"),
)
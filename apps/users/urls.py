from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "users"

urlpatterns = (
    path("logout/", auth_views.LogoutView.as_view(next_page="core:home"), name="logout"),
    path("admin-aid/create", views.create_admin_aid, name="create_admin_aid"),
    path("admin-aid/resend-email/<int:id>/", views.resend_setup_email, name="resend_setup_email"),
    path("admin-aid/<int:id>/toggle-status/", views.toggle_user_status, name="toggle_user_status"),
    path("account/setup/<str:token>", views.setup_account, name="setup_account"),
    path("register/office", views.office_register, name="office_register"),
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("verify-email/resend/<str:username>/", views.resend_verification_email, name="resend_verification_email"),
    path("register/office/status/<str:username>/", views.office_account_status, name="office_account_status"),
    path("register/office/reapply/<str:username>/", views.reapply_registration, name="reapply_registration"),
    path("admin/admin-aid-accounts/", views.list_admin_aid_accounts, name="list_admin_aid_accounts"),
    path("admin/registration-requests/", views.list_registration_requests, name="list_registration_requests"),
    path("admin/registration-requests/<int:id>/approve/", views.approve_registration_request, name="approve_registration_request"),
    path("admin/registration-requests/<int:id>/decline/", views.decline_registration_request, name="decline_registration_request"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("settings/", views.settings, name="settings"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("account_verification/", views.account_verification, name="account_verification"),
    path("change-password/<int:id>/", views.change_password, name="change_password"),
    path("email_sent/", views.email_sent, name="email_sent"),
    path("password_reset_success/", views.password_reset_success, name="password_reset_success"),
    path("forgot_password_success/", views.forgot_password_success, name="forgot_password_success"),
)
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views
from . forms import ChangePasswordForm, ResetPasswordForm, ConfirmResetPasswordForm

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

    # Change password url paths with built-in views
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            form_class=ChangePasswordForm,
            template_name="users/change-password.html",
            success_url=reverse_lazy("users:password_change_success")
        ),
        name="password_change"
    ),
    path(
        "password/change/success/", 
        auth_views.PasswordChangeDoneView.as_view(template_name="users/change-password-success.html"),
        name="password_change_success"
    ),

    # Reset password url paths with built-in views
    path(
        "password/reset/", 
        auth_views.PasswordResetView.as_view(
            form_class=ResetPasswordForm,
            template_name="users/password-reset-form.html",
            email_template_name="users/password-reset-email.html",
            success_url=reverse_lazy("users:password_reset_email_sent")
        ), 
        name="password_reset"
    ),
    path(
        "password/reset/email-sent/", 
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password-reset-email-sent.html"
        ), 
        name="password_reset_email_sent"
    ),
    path(
        "password/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            form_class=ConfirmResetPasswordForm,
            template_name="users/password-reset-confirm.html",
            success_url=reverse_lazy("users:password_reset_success")
        ),
        name="password_reset_confirm"
    ),
    path(
        "password/reset/success/", 
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password-reset-success.html"
        ), 
        name="password_reset_success"
    ),
)
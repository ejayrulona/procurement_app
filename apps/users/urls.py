from django.urls import path
from . import views

app_name = "users"

urlpatterns = (
    path("register_admin", views.register_admin, name="register_admin"),
    path("register_college/", views.register_college, name="register_college"),
    path("profile/", views.profile, name="profile"),
)
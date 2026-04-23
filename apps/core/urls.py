from django.urls import path
from . import views
from .views import HomeLoginView

app_name = "core"

urlpatterns = (
    path("", HomeLoginView.as_view(), name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
)
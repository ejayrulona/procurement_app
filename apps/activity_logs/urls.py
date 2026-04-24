from django.urls import path
from . import views

app_name = "activity_logs"

urlpatterns = (
    path("activity_log", views.activity_log, name="activity_log"),
)
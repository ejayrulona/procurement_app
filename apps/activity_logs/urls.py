from django.urls import path
from . import views

app_name = "activity_logs"

urlpatterns = (
    path("", views.list_activities, name="list_activities"),
)
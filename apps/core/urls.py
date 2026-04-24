from django.urls import path
from . import views

app_name = "core"

urlpatterns = (
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),

    


    
    path("college_dashboard/", views.college_dashboard, name="college_dashboard"),
)
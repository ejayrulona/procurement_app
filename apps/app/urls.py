from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path("create/", views.app_create, name="app_create"),
    path("create-final/", views.app_create_final, name="app_create_final"),
    path("apps/", views.app_list, name="app_list"),
    path("<int:id>/", views.app, name="app"),
    path("<int:id>/add-schedule/", views.app_add_schedule, name="app_add_schedule"),
    path("<int:id>/export/", views.export_app_excel, name="export_app_excel"),
]

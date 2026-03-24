from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = (
    path("", views.list_inventory, name="list_inventory"),
)
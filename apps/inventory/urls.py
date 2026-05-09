from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path("", views.item_list, name="item_list"),
    path("items/create/", views.item_create, name="item_create"),
    path("items/<int:id>/", views.item_detail, name="item_detail"),
    path("items/<int:id>/edit/", views.item_edit, name="item_edit"),
    path("api/get-object-codes/", views.get_object_codes, name="get_object_codes"),
    path("api/get-item-codes/", views.get_item_codes, name="get_item_codes"),
    path("add_object_expenditure/", views.add_object_expenditure, name="add_object_expenditure"),
    path("add_object_code/", views.add_object_code, name="add_object_code"),
    path("add_item_code/", views.add_item_code, name="add_item_code"),
]
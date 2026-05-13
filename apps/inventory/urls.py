from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path("", views.item_list, name="item_list"),
    path("items/create/", views.item_create, name="item_create"),
    path("items/<int:id>/", views.item_detail, name="item_detail"),
    path("items/<int:id>/edit/", views.item_edit, name="item_edit"),
    path("items/object-expenditure/add/", views.object_expenditure_add, name="object_expenditure_add"),
    path("items/object-code/add/", views.object_code_add, name="object_code_add"),
    path("items/item-code/add/", views.item_code_add, name="item_code_add"),
    path("api/get-object-codes/", views.get_object_codes, name="get_object_codes"),
    path("api/get-item-codes/", views.get_item_codes, name="get_item_codes"),
    path("api/get-all-item-codes/", views.get_all_item_codes, name="get_items_by_item_code"),
    path("api/get-items-by-item-code/", views.get_items_by_item_code, name="get_items_by_item_code"),
]
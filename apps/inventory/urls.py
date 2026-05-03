from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('inventory/', views.list_inventory, name='list_inventory'),
    path('view/<str:item_id>/', views.view_inventory_item, name='view_inventory_item'),
    path('edit/<str:item_id>/', views.edit_inventory_item, name='edit_inventory_item'),
]
from django.shortcuts import render

def list_inventory(request):
    return render(request, "inventory/inventory.html")

def view_inventory_item(request, item_id):
    context = {
        'item_id': item_id
    }
    return render(request, "inventory/inventory_detail_view.html", context)

def edit_inventory_item(request, item_id):
    context = {
        'item_id': item_id
    }
    return render(request, "inventory/inventory_edit.html", context)
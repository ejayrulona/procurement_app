from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import ObjectOfExpenditure, ObjectCode, ItemCode, Item
from .forms import ItemForm
from apps.users.decorators import any_admin_required

@any_admin_required
def item_list(request):
    items = Item.objects.all().order_by("-created_at")

    context = {
        "items": items,
    }

    return render(request, "inventory/items.html", context)

@any_admin_required
def item_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "Item added successfully.")
            return redirect("inventory:item_list")
        
    else:
        form = ItemForm()

    context = {
        "form": form,
        "object_of_expenditures": ObjectOfExpenditure.objects.all(),
    }

    return render(request, "inventory/create-item.html", context)

@any_admin_required
def item_edit(request, id):
    item = get_object_or_404(
        Item.objects.select_related(
            "item_code",
            "item_code__object_code",
            "item_code__object_code__expenditure"
        ),
        pk=id
    )

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)

        if form.is_valid():
            form.save()

            messages.success(request, "Item updated successfully.")
            return redirect("inventory:item_list")
        
        else:
            print(form.errors)
    else:
        form = ItemForm(instance=item)

    context = {
        "form": form,
        "object_of_expenditures": ObjectOfExpenditure.objects.all(),
    }
        
    return render(request, "inventory/edit-item.html", context)
        
@any_admin_required
def item_detail(request, id):
    item = get_object_or_404(
        Item.objects.select_related(
            "item_code",
            "item_code__object_code",
            "item_code__object_code__expenditure"
        ),
        pk=id
    )

    context = {
        "item": item,
    }

    return render(request, "inventory/item.html", context)

def get_object_codes(request):
    object_of_expenditure_id = request.GET.get('expenditure')
    object_codes = list(ObjectCode.objects.filter(expenditure=object_of_expenditure_id).values("id", "code"))
    return JsonResponse({"object_codes": object_codes})

def get_item_codes(request):
    object_code_id = request.GET.get('object-code')
    item_codes = list(ItemCode.objects.filter(object_code=object_code_id).values("id", "code", "general_description"))
    return JsonResponse({"item_codes": item_codes})
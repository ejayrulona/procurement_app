from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .importer import import_items_from_excel
from .forms import ObjectOfExpenditureForm, ObjectCodeForm, ItemCodeForm, ItemForm
from .models import ObjectOfExpenditure, ObjectCode, ItemCode, Item
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
def object_expenditure_add(request):
    if request.method == "POST":
        form = ObjectOfExpenditureForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "Object of expenditure added successfully.")
            return redirect("inventory:item_list")
        
    else:
        form = ObjectOfExpenditureForm()

    context = {
        "form": form
    }

    return render(request, "inventory/add-object-expenditure.html", context)


@any_admin_required
def object_code_add(request):
    if request.method == "POST":
        form = ObjectCodeForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "Object code added successfully.")
            return redirect("inventory:item_list")
        
    else:
        form = ObjectCodeForm()

    context = {
        "form": form,
        "expenditures": ObjectOfExpenditure.objects.all()
    }
        
    return render(request, "inventory/add-object-code.html", context)


@any_admin_required
def item_code_add(request):
    if request.method == "POST":
        form = ItemCodeForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "Item code added successfully.")
            return redirect("inventory:item_list")
        
    else:
        form = ItemCodeForm()

    context = {
        "form": form,
        "object_codes": ObjectCode.objects.all()
    }
        
    return render(request, "inventory/add-item-code.html", context)


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


def get_all_item_codes(request):
    item_codes = ItemCode.objects.select_related("object_code").all()

    data = [
        {
            "id": ic.id,
            "code": ic.code,
            "general_description": ic.general_description,
            "object_code_display": ic.object_code.code,
        }
        for ic in item_codes
    ]

    return JsonResponse({"item_codes": data})


def get_items_by_item_code(request):
    item_code_id = request.GET.get("item_code_id")

    if not item_code_id:
        return JsonResponse({"error": "item_code_id is required."}, status=400)

    item_code = get_object_or_404(ItemCode, pk=item_code_id)

    items = list(Item.objects.filter(item_code=item_code).values("id", "name", "specification", "unit", "unit_cost"))

    return JsonResponse({"items": items, "general_description": item_code.general_description})


@any_admin_required
def import_items(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return JsonResponse({"error": "No file uploaded."}, status=400)

        if not uploaded_file.name.endswith(".xlsx"):
            return JsonResponse(
                {"error": "Invalid file type. Please upload an .xlsx file."}, status=400
            )

        # 10MB limit
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse(
                {"error": "File too large. Maximum size is 10MB."}, status=400
            )

        result = import_items_from_excel(uploaded_file)

        return JsonResponse({
            "created": result.created,
            "updated": result.updated,
            "skipped": result.skipped,
            "errors": result.errors,
        }, status=200)

    return render(request, "inventory/import-items.html")
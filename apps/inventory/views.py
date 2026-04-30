from django.shortcuts import render

def inventory(request):
    return render(request, "inventory/inventory.html")
from django.shortcuts import render

def list_inventory(request):
    return render(request, "inventory/index.html")
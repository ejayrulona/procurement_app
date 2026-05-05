from django.shortcuts import render

# Create your views here.
def ppmp(request):
    return render(request, "ppmp/ppmp.html")
def ppmp_form(request):
    return render(request, "ppmp/ppmp_form.html")

def detailed_view(request):
    return render(request, "ppmp/detailed_view.html")

def request(request):
    return render(request, "ppmp/request.html")

def request_detail(request):
    return render(request, "ppmp/request_detail.html")

def list_page(request):
    return render(request, "ppmp/list_page.html")

def draft(request):
    return render(request, "ppmp/draft.html")


def app_procurement(request):
    return render(request, "ppmp/app-procurement.html")

def request_detail(request):
    return render(request, "ppmp/request_detail.html")

def app_list(request):
    return render(request, "ppmp/app-list.html")
from django.shortcuts import render

def home(request):
    return render(request, "core/home.html")

def dashboard(request):
    return render(request, "core/dashboard.html")

# Pwede mo na to remove mga naka comment, nilagay ko lang here sa core para ma view ko siya sa Web maayos, wag kalimutan remove din pati sa urls.py 

# def draft(request):
#     return render(request, "core/draft.html")

# def list_page(request):
#     return render(request, "core/list_page.html")

# def detailed_view(request):
#     return render(request, "core/detailed_view.html")

# def college_dashboard(request):
#     return render(request, "core/college_dashboard.html")

# def ppmp_form(request):
#     return render(request, "core/ppmp_form.html")

# def request(request):
#     return render(request, "core/request.html")

# def ppmp(request):
#     return render(request, "core/ppmp.html")

# def drafts(request):
#     return render(request, "core/drafts.html")

# def request_detail(request):
#     return render(request, "core/request_detail.html")












# def draft(request):
#     return render(request, "core/draft.html")

# def list_page(request):
#     return render(request, "core/list_page.html")

# def detailed_view(request):
#     return render(request, "core/detailed_view.html")

# def college_dashboard(request):
#     return render(request, "core/college_dashboard.html")

# def ppmp_form(request):
#     return render(request, "core/ppmp_form.html")

# def request(request):
#     return render(request, "core/request.html")

# def ppmp(request):
#     return render(request, "core/ppmp.html")

# def drafts(request):
#     return render(request, "core/drafts.html")

# def request_detail(request):
#     return render(request, "core/request_detail.html")

# def admin_registration(request):
#     return render(request, "core/admin_registration.html")

# def settings(request):
#     return render(request, "core/settings.html")
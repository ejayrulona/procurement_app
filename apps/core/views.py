from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

class HomeLoginView(LoginView):
    template_name = "core/home.html"

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect("core:dashboard")
        
        return super().dispatch(request, *args, **kwargs)

@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")

# Pwede mo na to remove mga naka comment, nilagay ko lang here sa core para ma view ko siya sa Web maayos, wag kalimutan remove din pati sa urls.py 
# def college_dashboard(request):
#     return render(request, "core/college_dashboard.html")

def ppmp(request):
    return render(request, "core/ppmp.html")

# def request_detail(request):
#     return render(request, "core/request_detail.html")










def college_dashboard(request):
    return render(request, "core/college_dashboard.html")

def ppmp_form(request):
    return render(request, "core/ppmp_form.html")

def request(request):
    return render(request, "core/request.html")

def drafts(request):
    return render(request, "core/drafts.html")
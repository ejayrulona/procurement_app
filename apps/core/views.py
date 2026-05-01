from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from apps.users.decorators import any_admin_required, college_required

class HomeLoginView(LoginView):
    template_name = "core/home.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_any_admin:
            return reverse_lazy("core:admin_dashboard")
        
        return reverse_lazy("core:college_dashboard")

@any_admin_required
def admin_dashboard(request):
    return render(request, "core/admin_dashboard.html")

@college_required
def college_dashboard(request):
    return render(request, "core/college_dashboard.html")
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

class HomeLoginView(LoginView):
    template_name = "core/home.html"

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect("core:dashboard")
        
        return super().dispatch(request, *args, **kwargs)

def dashboard(request):
    return render(request, "core/dashboard.html")
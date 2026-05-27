from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from apps.activity_logs.models import ActivityLog
from apps.inventory.models import Item
from apps.ppmp.models import ProcurementProjectManagementPlan
from apps.users.models import User
from apps.users.decorators import any_admin_required, office_required

class HomeLoginView(LoginView):
    template_name = "core/home.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_any_admin:
            return reverse_lazy("core:admin_dashboard")
        
        return reverse_lazy("core:office_dashboard")

def about(request):
    return render(request, 'core/about.html')

@any_admin_required
def admin_dashboard(request):
    pending_ppmps = ProcurementProjectManagementPlan.objects.filter(status=ProcurementProjectManagementPlan.Status.PENDING).count()
    pending_registrations = User.objects.filter(role=User.Role.OFFICE, is_active=False).count()
    total_items = Item.objects.count()
    total_ppmps = ProcurementProjectManagementPlan.objects.count()
    activities = ActivityLog.objects.prefetch_related("user").order_by("-timestamp")[:5]

    context = {
        "pending_ppmps": pending_ppmps,
        "pending_registrations": pending_registrations,
        "total_items": total_items,
        "total_ppmps": total_ppmps,
        "activities": activities,
    }
    
    return render(request, "core/admin_dashboard.html", context)

@office_required
def office_dashboard(request):
    return render(request, "core/office_dashboard.html")
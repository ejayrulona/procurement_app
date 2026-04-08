from django.urls import path
from . import views

app_name = "core"

urlpatterns = (
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # Pwede mo na to remove mga naka comment, nilagay ko lang here sa core para ma view ko siya sa Web maayos, wag kalimutan remove din pati sa views.py 
    # path("draft/", views.draft, name="draft"),
    # path("list_page/", views.list_page, name="list_page"),
    # path("detailed_view/", views.detailed_view, name="detailed_view"),
    # path("college_dashboard/", views.college_dashboard, name="college_dashboard"),
    # path("ppmp_form/", views.ppmp_form, name="ppmp_form"),
    # path("request/", views.request, name="request"),
    # path("request_detail/", views.request_detail, name="request_detail"),
    # path("ppmp/", views.ppmp, name="ppmp"),
    # path("drafts/", views.drafts, name="drafts"),
)
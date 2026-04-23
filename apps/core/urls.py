from django.urls import path
from . import views

app_name = "core"

urlpatterns = (
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("pending_accounts/", views.pending_accounts, name="pending_accounts"),
    path("request/", views.request, name="request"),
    path("draft/", views.draft, name="draft"),
    path("college_drafts/", views.college_drafts, name="college_drafts"),
    path("list_page/", views.list_page, name="list_page"),
    path("detailed_view/", views.detailed_view, name="detailed_view"),


    path("ppmp/", views.ppmp, name="ppmp"),
    path("college_dashboard/", views.college_dashboard, name="college_dashboard"),
)
from django.urls import path
from . import views

app_name = "ppmp"

urlpatterns = (
    path("request/", views.request, name="request"),
    path("request_detail/", views.request_detail, name="request_detail"),
    path("ppmp_form/", views.ppmp_form, name="ppmp_form"),
    path("ppmp/", views.ppmp, name="ppmp"),
    path("detailed_view/", views.detailed_view, name="detailed_view"),
    path("list_page/", views.list_page, name="list_page"),
    path("draft/", views.draft, name="draft"),
    path("app_procurement/", views.app_procurement, name="app_procurement"),
    path("app_list/", views.app_list, name="app_list"),
)

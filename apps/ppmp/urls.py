from django.urls import path
from . import views

app_name = "ppmp"

urlpatterns = (
    path("create/", views.ppmp_create, name="ppmp_create"),
    path("ppmp/<int:id>/", views.ppmp, name="ppmp"),
    path("ppmps/", views.ppmps, name="ppmps"),
    path("app_list/", views.app_list, name="app_list"),
    path("app/", views.app, name="app"),
    path("edit_ppmp/", views.edit_ppmp, name="edit_ppmp"),
)

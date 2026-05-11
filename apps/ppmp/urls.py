from django.urls import path
from . import views

app_name = "ppmp"

urlpatterns = (
    path("create/", views.ppmp_create, name="ppmp_create"),
    path("ppmp/<int:id>/", views.ppmp, name="ppmp"),
    path("ppmps/", views.ppmps, name="ppmps"),
    path("<int:id>/edit/", views.ppmp_edit, name="ppmp_edit"),
    path("<int:id>/approve/", views.ppmp_approve, name="ppmp_approve"),
    path("<int:id>/decline/", views.ppmp_decline, name="ppmp_decline"),
    path("app/create/", views.app_create, name="app_create"),
    path("apps/", views.app_list, name="app_list"),
    path("app/<int:id>/", views.app, name="app"),
)

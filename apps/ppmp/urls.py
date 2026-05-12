from django.urls import path
from . import views

app_name = "ppmp"

urlpatterns = (
    path("create/", views.ppmp_create, name="ppmp_create"),
    path("<int:id>/create-final/", views.ppmp_create_final, name="ppmp_create_final"),
    path("ppmp/<int:id>/", views.ppmp, name="ppmp"),
    path("ppmps/", views.ppmps, name="ppmps"),
    path("<int:id>/edit/", views.ppmp_edit, name="ppmp_edit"),
    path("<int:id>/approve/", views.ppmp_approve, name="ppmp_approve"),
    path("<int:id>/decline/", views.ppmp_decline, name="ppmp_decline"),
    path("<int:id>/revise/", views.ppmp_revise, name="ppmp_revise"),
    path("app/create/", views.app_create, name="app_create"),
    path("apps/", views.app_list, name="app_list"),
    path("app/<int:id>/", views.app, name="app"),
    path("edit_app", views.edit_app, name="edit_app"),
)

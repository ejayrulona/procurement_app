from django.urls import path
from . import views
from .views import HomeLoginView

app_name = "core"

urlpatterns = (
    path("", HomeLoginView.as_view(), name="home"),
    path("procurement/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("office/dashboard/", views.office_dashboard, name="office_dashboard"),
    path('about/', views.about, name='about'),
)
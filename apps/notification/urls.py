from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [
        path("", views.notification_list, name="notification_list"),
        path("<int:id>/mark-read/", views.mark_read, name="mark_read"),
        path("mark-all-read/", views.mark_all_read, name="mark_all_read"),
        path("<int:id>/delete/", views.delete_notification, name="delete_notification"),
        path("clear-all/", views.clear_all, name="clear_all"),
]
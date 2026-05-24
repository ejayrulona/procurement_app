from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)

    context = {
        "notifications": notifications,
        "unread_count":  notifications.filter(is_read=False).count(),
    }

    return render(request, "notification/notification.html", context)


@login_required
@require_POST
def mark_read(request, id):
    notification = get_object_or_404(Notification, pk=id, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])

    return redirect("notification:notification_list")


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False,).update(is_read=True)
    return redirect("notification:notification_list")


@login_required
@require_POST
def delete_notification(request, id):
    notification = get_object_or_404(Notification, pk=id, recipient=request.user)
    notification.delete()

    return redirect("notification:notification_list")


@login_required
@require_POST
def clear_all(request):                          
    Notification.objects.filter(recipient=request.user).delete()
    return redirect("notification:notification_list")
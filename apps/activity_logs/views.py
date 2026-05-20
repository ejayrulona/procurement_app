from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ActivityLog

@login_required
def activity_log(request):
    if request.user.is_any_admin:
        activities = ActivityLog.objects.prefetch_related("user").order_by("-timestamp")
        user_activities = activities.filter(target_type=ActivityLog.TargetType.USER).count()
        item_activities = activities.filter(target_type=ActivityLog.TargetType.ITEM).count()
        app_activities = activities.filter(target_type=ActivityLog.TargetType.APP).count()
    else:
        activities = ActivityLog.objects.filter(user=request.user).prefetch_related("user").order_by("-timestamp")

    total_activities = activities.count()
    ppmp_activities = activities.filter(target_type=ActivityLog.TargetType.PPMP).count()

    context = {
        "activities": activities,
        "total_activities": total_activities,
        "ppmp_activities": ppmp_activities,
    }

    if request.user.is_any_admin:
        context.update({
            "user_activities": user_activities,
            "item_activities": item_activities,
            "app_activities": app_activities,
        })

    return render(request, "activity_logs/activity_log.html", context)
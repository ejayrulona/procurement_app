from django.shortcuts import render
from .models import ActivityLog

def activity_log(request):
    activities = ActivityLog.objects.prefetch_related("user").order_by("-timestamp")

    total_activities = activities.count()
    user_activities = activities.filter(target_type=ActivityLog.TargetType.USER).count()
    item_activities = activities.filter(target_type=ActivityLog.TargetType.ITEM).count()
    ppmp_activities = activities.filter(target_type=ActivityLog.TargetType.PPMP).count()
    app_activities = activities.filter(target_type=ActivityLog.TargetType.APP).count()

    context = {
        "activities": activities,
        "total_activities": total_activities,
        "user_activities": user_activities,
        "item_activities": item_activities,
        "ppmp_activities": ppmp_activities,
        "app_activities": app_activities,
    }
    return render(request, "activity_logs/activity_log.html", context)
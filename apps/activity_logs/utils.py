from .models import ActivityLog

def log_activity(
    *,
    user,
    action,
    target_type,
    target_id=None,
    target_label="",
    remarks=None,
    changes=None,
):
    ActivityLog.objects.create(
            user = user,
            user_full_name = user.full_name or user.username,
            user_role = getattr(user, "role", ""),
            action = action,
            target_type = target_type,
            target_id = target_id,
            target_label = target_label,
            remarks = remarks,
            changes = changes,
        )
from .models import Notification
from apps.activity_logs.models import ActivityLog

_NOTIFICATION_MAP = {
    ActivityLog.Action.APPROVE_PPMP: (
        Notification.Type.PPMP_APPROVED,
        lambda **kwargs: (
            "PPMP approved",
            f"Your PPMP \"{kwargs['target_label']}\" has been approved.",
        ),
    ),
    ActivityLog.Action.DECLINE_PPMP: (
        Notification.Type.PPMP_DECLINED,
        lambda **kwargs: (
            "PPMP declined",
            f"Your PPMP \"{kwargs['target_label']}\" has been declined."
            + (f" Reason: {kwargs['remarks']}" if kwargs.get("remarks") else ""),
        ),
    ),
    ActivityLog.Action.SET_REVISION_PPMP: (
        Notification.Type.PPMP_SET_FOR_REVISION,
        lambda **kwargs: (
            "PPMP set for revision",
            f"Your PPMP \"{kwargs['target_label']}\" has been sent back for revision."
            + (f" Note: {kwargs['remarks']}" if kwargs.get("remarks") else ""),
        ),
    ),
}


def notify_user(
    *,
    recipient,
    action,
    target_label="",
    target_type="",
    target_id=None,
    remarks=None,
    actor_name="",
):
    entry = _NOTIFICATION_MAP.get(action)
    if entry is None:
        return  # Action does not trigger a notification

    notification_type, message_builder = entry
    title, message = message_builder(
        target_label = target_label,
        remarks      = remarks,
        actor_name   = actor_name,
    )

    Notification.objects.create(
        recipient         = recipient,
        notification_type = notification_type,
        title             = title,
        message           = message,
        target_type       = target_type,
        target_id         = target_id,
    )
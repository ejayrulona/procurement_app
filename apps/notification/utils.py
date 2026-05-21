from .models import Notification

_MESSAGE_MAP = {
    Notification.Type.PPMP_APPROVED: lambda **kwargs: (
        "PPMP approved",
        f"Your PPMP \"{kwargs['target_label']}\" has been approved.",
    ),
    Notification.Type.PPMP_DECLINED: lambda **kwargs: (
        "PPMP declined",
        f"Your PPMP \"{kwargs['target_label']}\" has been declined."
        + (f" Reason: {kwargs['remarks']}" if kwargs.get("remarks") else ""),
    ),
    Notification.Type.PPMP_SET_FOR_REVISION: lambda **kwargs: (
        "PPMP set for revision",
        f"Your PPMP \"{kwargs['target_label']}\" has been sent back for revision."
        + (f" Note: {kwargs['remarks']}" if kwargs.get("remarks") else ""),
    ),
}


def notify_user(
    *,
    recipient,
    notification_type,
    target_label="",
    remarks=None,
    actor_name="",
):
    entry = _MESSAGE_MAP.get(notification_type)
    if entry is None:
        return

    title, message = entry(
        target_label = target_label,
        remarks = remarks,
        actor_name = actor_name,
    )

    Notification.objects.create(
        recipient = recipient,
        notification_type = notification_type,
        title = title,
        message = message,
    )
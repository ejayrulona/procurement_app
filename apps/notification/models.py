from django.db import models

class Notification(models.Model):

    class Type(models.TextChoices):
        PPMP_APPROVED = "ppmp_approved", "PPMP approved"
        PPMP_DECLINED = "ppmp_declined", "PPMP declined"
        PPMP_SET_FOR_REVISION = "ppmp_set_for_revision", "PPMP set for revision"

    recipient = models.ForeignKey("users.User",on_delete=models.CASCADE,related_name="notifications")
    notification_type = models.CharField(max_length=50, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes  = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["timestamp"]),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"[{'Read' if self.is_read else 'Unread'}] {self.recipient} — {self.title}"
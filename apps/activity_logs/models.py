from django.db import models

class ActivityLog(models.Model):
    class Action(models.TextChoices):
        # User registration
        APPROVE_REGISTRATION = "approve_registration", "Approved user registration"
        DECLINE_REGISTRATION = "decline_registration", "Declined user registration"

        # Account management
        CREATE_ADMIN_AID_ACCOUNT = "create_admin_aid_account", "Created admin aid account"
        ACTIVATE_AID_ACCOUNT = "activate_aid_account", "Activated aid account"
        DEACTIVATE_AID_ACCOUNT = "deactivate_aid_account", "Deactivated aid account"
        RESEND_SETUP_EMAIL = "resend_setup_email", "Resend aid account setup email"

        # Item management
        ADD_ITEM = "add_item", "Added item"
        UPDATE_ITEM = "update_item", "Updated item"

        # PPMP
        CREATE_PPMP = "create_ppmp", "Created PPMP"
        EDIT_PPMP = "edit_ppmp", "Edited PPMP"
        APPROVE_PPMP = "approve_ppmp", "Approved PPMP"
        DECLINE_PPMP = "decline_ppmp", "Declined PPMP"
        SET_REVISION_PPMP = "set_revision_ppmp", "Set PPMP for revision"

        # APP
        CREATE_APP = "CREATE_APP", "Created APP"

    class TargetType(models.TextChoices):
        USER = "USER", "User"
        ITEM = "ITEM", "Item"
        PPMP = "PPMP", "PPMP"
        APP  = "APP",  "APP"

    user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="activity_logs")
    user_full_name = models.CharField(max_length=120)
    user_role = models.CharField(max_length=20)   
    action = models.CharField(max_length=50, choices=Action.choices)
    target_type = models.CharField(max_length=50, choices=TargetType.choices)
    target_id = models.PositiveIntegerField(null=True, blank=True)   
    target_label = models.CharField(max_length=255, blank=True) # e.g "Engineering - 2026 (Final)" or "John Doe" 
    remarks = models.TextField(null=True, blank=True)   
    changes = models.JSONField(null=True, blank=True)   
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["action"]),
            models.Index(fields=["target_type", "target_id"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user_full_name} — {self.get_action_display()}"
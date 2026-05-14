from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

MOOE_THRESHOLD = Decimal("50000.00")

class ModeOfProcurement(models.TextChoices):
    COMPETETIVE_BIDDING = "competitive_bidding", "Competitive Bidding"
    LIMITED_SOURCE_BIDDING = "limited_source_bidding", "Limited Source Bidding"
    DIRECT_CONTRACTING = "direct_contracting", "Direct Contracting"
    REPEAT_ORDER = "repeat_order", "Repeat Order"
    SMALL_VALUE_PROCUREMENT = "small_value_procurement", "Small Value Procurement"
    SHOPPING = "shopping", "Shopping"
    NEGOTIATED_PROCUREMENT = "negotiated_procurement", "Negotiated Procurement"


class ProcurementProjectManagementPlan(models.Model):
    class Classification(models.TextChoices):
        GOODS = "goods", "Goods"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        CONSULTING_SERVICES = "consulting_services", "Consulting Services"


    class SourceOfFunds(models.TextChoices):
        GAA = "gaa", "General Appropriations Act (GAA)"
        IGF = "igf", "Internally Generated Funds (IGF)"
        TRUST_FUND = "trust_fund", "Trust Fund"
        FAP = "fap", "Foreign Assisted Project (FAP)"
        SPECIAL_ACCOUNT = "special_account", "Special Account"
        LOCAL_FUNDS = "local_funds", "Local Funds"
        SPECIAL_TRUST_FUND = "special_trust_fund", "STF/101"


    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        FOR_REVISION = "for_revision", "For Revision"


    class SubmissionType(models.TextChoices):
        INDICATIVE = "indicative", "Indicative"
        FINAL = "final", "Final"


    office_profile = models.ForeignKey("users.OfficeProfile", on_delete=models.PROTECT, related_name="ppmps")
    fiscal_year = models.PositiveIntegerField()
    submission_type = models.CharField(max_length=15, choices=SubmissionType.choices, default=SubmissionType.INDICATIVE)
    classification = models.CharField(max_length=30, choices=Classification.choices)
    source_of_funds = models.CharField(max_length=30, choices=SourceOfFunds.choices)
    ceiling = models.DecimalField(max_digits=14, decimal_places=2)
    submitted_by = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="submitted_ppmps")
    reviewed_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_ppmps")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    remarks = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PPMP"
        verbose_name_plural = "PPMPs"
        ordering = ["-created_at"]

        # One PPMP per office per fiscal year per classification
        constraints = [
            models.UniqueConstraint(
                fields=["office_profile", "fiscal_year", "classification", "submission_type"],
                name="unique_ppmp_per_office_per_fiscal_year_per_classification_per_submission_type"
            )
        ]


    def __str__(self):
        return f"{self.office_profile.office_name} - {self.get_classification_display()} - FY: {self.fiscal_year}"
    
    @property
    def total_amount(self):
        return sum(line.total_amount for line in self.procurement_lines.prefetch_related("line_entries__item").all())
    
    @property
    def has_exceeded_ceiling(self):
        return self.total_amount > self.ceiling
    
    @classmethod
    def annotated_queryset(cls):
        return cls.objects.annotate(
            computed_total=Sum(
                ExpressionWrapper(
                    F("procurement_lines__line_entries__quantity") *
                    F("procurement_lines__line_entries__item__unit_cost"),
                    output_field=DecimalField()
                )
            )
        )
    
    def clean(self):
        if self.pk and self.has_exceeded_ceiling:
            raise ValidationError("PPMP total amount has exceeded the ceiling. Please review your procurement lines.")
        

class ProcurementLine(models.Model):
    ppmp = models.ForeignKey(ProcurementProjectManagementPlan, on_delete=models.CASCADE, related_name="procurement_lines")
    item_code = models.ForeignKey("inventory.ItemCode", on_delete=models.PROTECT, related_name="procurement_lines")
    mode_of_procurement = models.CharField(max_length=30, choices=ModeOfProcurement.choices)
    procurement_program = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Procurement Line"
        verbose_name_plural = "Procurement Lines"
        ordering = ["order"]


    def __str__(self):
        return f"{self.ppmp} | Line {self.order}: {self.item_code.general_description}"

    @property
    def mooe_total(self):
        """Sum of totals for entries where unit_cost_snapshot < 50,000."""

        return sum(
            entry.quantity * entry.unit_cost_snapshot
            for entry in self.line_entries.all()
            if entry.unit_cost_snapshot < MOOE_THRESHOLD
        )

    @property
    def co_total(self):
        """Sum of totals for entries where unit_cost_snapshot >= 50,000."""
        
        return sum(
            entry.quantity * entry.unit_cost_snapshot
            for entry in self.line_entries.all()
            if entry.unit_cost_snapshot >= MOOE_THRESHOLD
        )

    @property
    def total_amount(self):
        return sum(
            entry.total_amount
            for entry in self.line_entries.select_related("item").all()
        )
    

class ProcurementLineEntry(models.Model):
    procurement_line = models.ForeignKey(ProcurementLine, on_delete=models.CASCADE, related_name="line_entries")
    item = models.ForeignKey("inventory.Item", on_delete=models.PROTECT, related_name="line_entries")

    # Snapshot unit cost at time of entry — protects against future item price changes
    unit_cost_snapshot = models.DecimalField(max_digits=12, decimal_places=2)

    quantity = models.PositiveIntegerField()
    date_needed = models.DateField()
    remarks = models.TextField(blank=True)

    class Meta:
        verbose_name = "Procurement Line Entry"
        verbose_name_plural = "Procurement Line Entries"
        
        # Prevent duplicate item entries within the same procurement line
        constraints = [
            models.UniqueConstraint(
                fields=["procurement_line", "item"],
                name="unique_item_per_procurement_line"
            )
        ]


    def __str__(self):
        return f"{self.item.name} x{self.quantity} — {self.procurement_line}"

    @property
    def total_amount(self):
        return self.quantity * self.unit_cost_snapshot

    def save(self, *args, **kwargs):
        # Snapshots the unit cost from the item at time of saving
        if not self.unit_cost_snapshot:
            self.unit_cost_snapshot = self.item.unit_cost
        super().save(*args, **kwargs)
from django.db import models

class AnnualProcurementPlan(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    class SubmissionType(models.TextChoices):
        INDICATIVE = "indicative", "Indicative"
        FINAL = "final", "Final"

    fiscal_year = models.PositiveIntegerField()
    submission_type = models.CharField(max_length=15, choices=SubmissionType.choices, default=SubmissionType.INDICATIVE)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    prepared_by = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="prepared_apps")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Annual Project Plan"
        verbose_name_plural = "Annual Project Plans"
        ordering = ["-fiscal_year"]

        constraints = [
            models.UniqueConstraint(
                fields=["fiscal_year", "submission_type"],
                name="unique_app_per_fiscal_year_per_submission_type"
            )
        ]

    
    def __str__(self):
        return f"APP - FY{self.fiscal_year}"
    
    @property
    def grand_total(self):
        return sum(entry.total for entry in self.app_entries.all())
    
    @property
    def grand_total_mooe(self):
        return sum(entry.mooe for entry in self.app_entries.all())
    
    @property
    def grand_total_co(self):
        return sum(entry.co for entry in self.app_entries.all())
    

class AnnualProcurementPlanEntry(models.Model):
    app = models.ForeignKey(AnnualProcurementPlan, on_delete=models.CASCADE, related_name="app_entries")
    ppmp = models.OneToOneField("ppmp.ProcurementProjectManagementPlan", on_delete=models.PROTECT, related_name="app_entry")

    # Schedule for Each Procurement Activity
    advertisement_date = models.DateField(null=True, blank=True, verbose_name="Advertisement/Posting of IB/REI")
    submission_date = models.DateField(null=True, blank=True, verbose_name="Submission/Opening of Bids")
    notice_of_award_date = models.DateField(null=True, blank=True, verbose_name="Notice of Award")
    contract_signing_date = models.DateField(null=True, blank=True, verbose_name="Contract Signing")

    # Estimated Budget Breakdown
    mooe = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="MOOE")
    co = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="CO")

    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "APP Entry"
        verbose_name_plural = "APP Entries"
        ordering = ["created_at"]


    def __str__(self):
        return f"{self.app} | {self.ppmp.office_profile.office_name}"
    
    @property
    def total(self):
        return self.mooe + self.co
    
    @property
    def pmo_end_user(self):
        return self.ppmp.office_profile.office_name
    
    @property
    def source_of_funds(self):
        return self.ppmp.get_source_of_funds_display()
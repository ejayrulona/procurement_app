from django.contrib import admin
from .models import AnnualProcurementPlan, AnnualProcurementPlanEntry

# Register your models here.
admin.site.register(AnnualProcurementPlan)
admin.site.register(AnnualProcurementPlanEntry)
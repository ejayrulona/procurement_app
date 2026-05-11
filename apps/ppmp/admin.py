from django.contrib import admin
from . models import (
    ProcurementProjectManagementPlan, ProcurementLine, ProcurementLineEntry, AnnualProcurementPlan,
    AnnualProcurementPlanEntry
)

admin.site.register(ProcurementProjectManagementPlan)
admin.site.register(ProcurementLine)
admin.site.register(ProcurementLineEntry)
admin.site.register(AnnualProcurementPlan)
admin.site.register(AnnualProcurementPlanEntry)
from django.contrib import admin
from . models import ProcurementProjectManagementPlan, ProcurementLine, ProcurementLineEntry

admin.site.register(ProcurementProjectManagementPlan)
admin.site.register(ProcurementLine)
admin.site.register(ProcurementLineEntry)
from django.contrib import admin
from . models import CollegeOffice, AdminProfile, CollegeProfile 

# Register your models here.

admin.site.register(CollegeOffice)
admin.site.register(AdminProfile)
admin.site.register(CollegeProfile)
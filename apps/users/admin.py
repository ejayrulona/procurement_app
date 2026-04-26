from django.contrib import admin
from .models import CollegeOffice, User, AdminProfile, CollegeProfile, RegistrationRequest 

# Register your models here.

admin.site.register(CollegeOffice)
admin.site.register(User)
admin.site.register(AdminProfile)
admin.site.register(CollegeProfile)
admin.site.register(RegistrationRequest)
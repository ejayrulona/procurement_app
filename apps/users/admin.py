from django.contrib import admin
from .models import (
    User, AdminProfile, OfficeProfile, RegistrationRequest, AccountSetupToken, EmailVerificationToken
)

admin.site.register(User)
admin.site.register(AdminProfile)
admin.site.register(OfficeProfile)
admin.site.register(RegistrationRequest)
admin.site.register(AccountSetupToken)
admin.site.register(EmailVerificationToken)
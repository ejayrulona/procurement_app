from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("A username is required")
        
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("email_verified", False)
        extra_fields.setdefault("role", User.Role.OFFICE)
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("role", User.Role.ADMIN)

        return self.create_user(username, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        ADMIN_AID = "admin_aid", "Admin Aid"
        OFFICE = "office", "Office"

    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=15, choices=Role.choices)
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, null=True, blank=True)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    email_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_adminaid(self):
        return self.role == self.Role.ADMIN_AID
    
    @property
    def is_office(self):
        return self.role == self.Role.OFFICE
    
    @property
    def is_any_admin(self):
        return self.role in [self.Role.ADMIN, self.Role.ADMIN_AID]

    @property
    def full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]

        return " ".join(part for part in parts if part)
    
    def __str__(self):
        return f"{self.full_name}, ({self.username})"
    
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin_profile")
    employee_id_number = models.CharField(max_length=50, unique=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", null=True, blank=True)
    is_setup_complete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"


    def __str__(self):
        return f"{self.user.role} - {self.user.full_name}"


class OfficeProfile(models.Model):
    class PAPCategory(models.TextChoices):
        ADMIN = "administration", "Administration"
        HIGHER_EDUCATION = "higher_education", "Higher Education"
        RESEARCH = "research", "Research"
        EXTENSION = "extension", "Extension"
        INCOME_GENERATING_PROJECT = "income_generating_project", "Income Generating Project"
        FIDUCIARY = "fiduciary", "Fiduciary"
        OUTSOURCING = "outsourcing", "Outsourcing"


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="office_profile")
    pap_category = models.CharField(max_length=30, choices=PAPCategory.choices)
    office_name = models.CharField(max_length=150)
    office_logo = models.ImageField(upload_to="office_logos/", null=True, blank=True)

    # Secretary Information (Contact Person & Optional only)
    secretary_full_name = models.CharField(max_length=150, blank=True)
    secretary_email = models.EmailField(blank=True)
    secretary_phone_number = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Office Profile"
        verbose_name_plural = "Office Profiles"


    def __str__(self):
        return f"{self.get_pap_category_display()} - {self.office_name} - {self.user.full_name}"  


class RegistrationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="registration_requests")
    is_latest = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_requests")

    class Meta: 
        verbose_name = "Registration Request"
        verbose_name_plural = "Registration Requests"
        ordering = ["-created_at"]

    
    def __str__(self):
        return f"{self.user.full_name} - {self.status}"
    

class AccountSetupToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="setup_token")
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Account Setup Token"
        verbose_name_plural = "Account Setup Tokens"


    def __str__(self):
        return f"Setup token for {self.user.full_name}"
    
    @property
    def is_expired(self):
        return timezone.now > self.expires_at
    

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_token")
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Email Verification Token"
        verbose_name_plural = "Email Verification Tokens"


    def __str__(self):
        return f"Email verification token for {self.user.full_name}"
    
    @property
    def is_expired(self):
        return timezone.now > self.expires_at
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CollegeOffice(models.Model):
    class OrganizationType(models.TextChoices):
        COLLEGE = "college", "College"
        DEPARTMENT = "department", "Department"
        OFFICE = "office", "Office"

    
    class Campus(models.TextChoices):
        CAMPUS_A = "A", "Campus A"
        CAMPUS_B = "B", "Campus B"
        CAMPUS_C = "C", "Campus C"


    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    organization_type = models.CharField(max_length=10, choices=OrganizationType.choices)
    campus = models.CharField(max_length=10, choices=Campus.choices)
    address = models.TextField()
    college_photo = models.ImageField(upload_to="college_photos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "College / Office"
        verbose_name_plural = "Colleges / Offices"


    def __str__(self):
        return f"{self.code} - {self.name}"
    

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("A username is required")
        
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_admin", False)
        
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(username, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=50, unique=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=80)
    middle_name = models.CharField(max_length=80, null=True, blank=True)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        

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

    class Meta:
        verbose_name = "Admin Profile"
        verbose_name_plural = "Admin Profiles"


    def __str__(self):
        return f"Admin - {self.user.full_name}"


class CollegeProfile(models.Model):
    class PositionTitle(models.TextChoices):
        DEAN = "dean", "Dean"
        ASSOCIATE_DEAN = "associate_dean", "Associate Dean"
        DEPT_HEAD = "department_head", "Department Head"
        DIRECTOR = "director", "Director"
        ASSOCIATE_DIRECTOR = "associate_director", "Associate Director"
        COORDINATOR = "coordinator", "Coordinator"
        CHAIRPERSON = "chairperson", "Chairperson"
        OFFICER_IN_CHARGE = "officer_in_charge", "OIC - Officer in Charge"
        PROGRAM_HEAD = "program_head", "Program Head"
        UNIT_HEAD = "unit_head", "Unit Head"
        DIVISION_CHIEF = "division_chief", "Division Head"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="college_profile")
    college_office = models.OneToOneField(CollegeOffice, on_delete=models.PROTECT, related_name="users")
    position_title = models.CharField(max_length=30, choices=PositionTitle.choices)

    class Meta:
        verbose_name = "College Profile"
        verbose_name_plural = "College Profiles"


    def __str__(self):
        return f"{self.college_office.name} - {self.user.full_name}"    
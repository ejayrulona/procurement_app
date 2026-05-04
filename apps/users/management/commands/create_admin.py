from django.core.management.base import BaseCommand
from apps.users.models import User, AdminProfile

class Command(BaseCommand):
    help = "Creates admin account for the procurement system"

    def handle(self, *args, **kwargs):
        if User.objects.filter(role=User.Role.ADMIN).exists():
            self.stdout.write("A admin account already exists.")
            return
        
        user = User.objects.create_user(
            username = "admin",
            role = User.Role.ADMIN,
            first_name = "Procurement",
            last_name = "Admin",
            email = "admin@wmsu.edu.ph",
            phone_number = "",
            email_verified = True,
            is_active = True,
            password = "admin12345"
        )

        AdminProfile.objects.create(
            user = user,
            employee_id_number = "2022-00779" # Student id number used as a temporary value for now, to be updated to use employee id number
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Admin created."
            )
        )
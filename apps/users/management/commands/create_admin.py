from django.core.management.base import BaseCommand
from users.models import User, AdminProfile

class Command(BaseCommand):
    help = "Creates admin account for the procurement system"

    def handle(self, *args, **kwargs):
        if User.objects.filter(role=User.Role.ADMIN).exists():
            self.stdout.write("A admin account already exists.")
            return
        
        user = User.objects.create(
            username = "admin",
            role = User.Role.ADMIN,
            first_name = "Procurement",
            last_name = "Admin",
            email = "admin@wmsu.edu.ph",
            phone_number = "",
            is_active = True,
            password = "admin12345"
        )

        AdminProfile.objects.create(
            user = user,
            employee_id_number = "" # Add the id number before running the command.
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Admin created."
            )
        )
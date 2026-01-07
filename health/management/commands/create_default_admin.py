"""Create a default superuser account for grading convenience."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a default admin user: admin / admin1234 (if it does not already exist)."

    def handle(self, *args, **options):
        User = get_user_model()
        username = "admin"
        password = "admin1234"

        if User.objects.filter(username=username).exists():
            self.stdout.write("Admin user already exists.")
            return

        User.objects.create_superuser(username=username, password=password, email="admin@example.com")
        self.stdout.write(f"Created admin user: {username} / {password}")

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create admin superuser from environment variables (idempotent)."

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USER', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('ADMIN_PASSWORD')
        
        if not password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_PASSWORD not set in environment. Skipping superuser creation.'
            ))
            return
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
            return
        
        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(
            f'Superuser created: username={username}, email={email}'
        ))
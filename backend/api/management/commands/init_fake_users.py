"""
Management command to initialize fake users in the database
Run: python manage.py init_fake_users
"""
from django.core.management.base import BaseCommand
from api.fake_user_manager import initialize_fake_users


class Command(BaseCommand):
    help = 'Initialize fake users in the database'

    def handle(self, *args, **options):
        self.stdout.write('Initializing fake users...')
        try:
            initialize_fake_users()
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully initialized all fake users!'
                )
            )
            
            # Show count
            from api.models import FakeUser
            count = FakeUser.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Total fake users in database: {count}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing fake users: {str(e)}')
            )


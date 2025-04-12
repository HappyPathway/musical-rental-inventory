from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rentals.models import Customer

class Command(BaseCommand):
    help = 'Create Customer records for users that have a user_type of customer but no Customer record'

    def handle(self, *args, **options):
        created_count = 0
        
        # Get all users
        for user in User.objects.all():
            # Check if they have a profile and are a customer
            if hasattr(user, 'profile') and user.profile.user_type == 'customer':
                # Check if they don't already have a customer record
                if not Customer.objects.filter(user=user).exists():
                    # Create a customer record for them
                    customer = Customer.objects.create(
                        user=user,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        phone=getattr(user.profile, 'phone_number', ''),
                        address=getattr(user.profile, 'address', ''),
                        city=getattr(user.profile, 'city', ''),
                        state=getattr(user.profile, 'state', ''),
                        zip_code=getattr(user.profile, 'zip_code', ''),
                        id_type='drivers_license',  # Default value
                        id_number=f"USER{user.id}",  # Default value
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created customer record for {user.username}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} customer records')
        )
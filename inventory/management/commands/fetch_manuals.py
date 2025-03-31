from django.core.management.base import BaseCommand
from inventory.models import Equipment
from inventory.utils import download_and_store_manual

class Command(BaseCommand):
    help = 'Test fetching manuals for equipment items'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='Equipment ID to fetch manual for')
        parser.add_argument('--all', action='store_true', help='Fetch manuals for all equipment')

    def handle(self, *args, **options):
        if options['id']:
            # Fetch manual for specific equipment
            try:
                equipment = Equipment.objects.get(id=options['id'])
                self.stdout.write(f"Fetching manual for {equipment.brand} {equipment.model_number}")
                result = download_and_store_manual(equipment)
                if result:
                    self.stdout.write(self.style.SUCCESS(f"Successfully fetched manual: {result}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Could not fetch manual"))
            except Equipment.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Equipment with ID {options['id']} not found"))
        
        elif options['all']:
            # Fetch manuals for all equipment with model numbers but no manuals yet
            equipment_list = Equipment.objects.filter(model_number__isnull=False, manual_file='')
            total = equipment_list.count()
            success = 0
            
            self.stdout.write(f"Found {total} equipment items without manuals")
            
            for equipment in equipment_list:
                self.stdout.write(f"Fetching manual for {equipment.brand} {equipment.model_number}")
                result = download_and_store_manual(equipment)
                if result:
                    success += 1
                    self.stdout.write(self.style.SUCCESS(f"Successfully fetched manual"))
                
            self.stdout.write(f"Fetched {success} out of {total} manuals")
        
        else:
            self.stdout.write("Please specify either --id or --all")
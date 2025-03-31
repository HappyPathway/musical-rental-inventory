from django.core.management.base import BaseCommand
from inventory.models import Equipment
from inventory.utils import download_and_store_manual

class Command(BaseCommand):
    help = 'Test fetching manuals for equipment items'

    def add_arguments(self, parser):
        parser.add_argument('--id', type=int, help='Equipment ID to fetch manual for')
        parser.add_argument('--model', type=str, help='Model number to search for')

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
        
        elif options['model']:
            # Find equipment by model number
            equipment_list = Equipment.objects.filter(model_number__icontains=options['model'])
            if not equipment_list.exists():
                self.stdout.write(self.style.ERROR(f"No equipment found with model number containing '{options['model']}'"))
                return
                
            for equipment in equipment_list:
                self.stdout.write(f"Found {equipment.brand} {equipment.model_number} (ID: {equipment.id})")
                self.stdout.write(f"Fetching manual...")
                result = download_and_store_manual(equipment)
                if result:
                    self.stdout.write(self.style.SUCCESS(f"Successfully fetched manual: {result}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Could not fetch manual"))
        
        else:
            self.stdout.write("Please specify either --id or --model")
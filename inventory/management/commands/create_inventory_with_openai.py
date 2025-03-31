import os
import json
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from inventory.models import Equipment, Category
from django.core.serializers import serialize
import openai

class Command(BaseCommand):
    help = 'Create inventory items with OpenAI assistance for pricing and categorization'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Equipment name')
        parser.add_argument('--description', type=str, help='Equipment description')
        parser.add_argument('--brand', type=str, help='Equipment brand')
        parser.add_argument('--model', type=str, help='Model number', default='')
        parser.add_argument('--serial', type=str, help='Serial number', default='')
        parser.add_argument('--purchase-date', type=str, help='Purchase date (YYYY-MM-DD)', default=None)
        parser.add_argument('--purchase-price', type=float, help='Purchase price', default=None)
        parser.add_argument('--category', type=str, help='Category name (will create if it doesn\'t exist)')
        parser.add_argument('--condition', type=str, help='Equipment condition', default='')
        parser.add_argument('--notes', type=str, help='Additional notes', default='')
        parser.add_argument('--api-key', type=str, help='OpenAI API key (if not set in environment)')
        parser.add_argument('--save-fixture', action='store_true', help='Save result as a fixture')
        parser.add_argument('--batch', type=str, help='Path to JSON file with multiple items to process')

    def handle(self, *args, **options):
        # Check for OpenAI API key
        api_key = options.get('api_key') or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            self.stderr.write(
                self.style.ERROR('OpenAI API key is required. Set it with --api-key or OPENAI_API_KEY environment variable.')
            )
            return

        openai.api_key = api_key

        # Process batch file if specified
        if options.get('batch'):
            return self.process_batch(options.get('batch'), options.get('save_fixture', False))

        # Process single item
        if not all([options.get('name'), options.get('description'), options.get('brand'), options.get('category')]):
            self.stderr.write(
                self.style.ERROR('Required fields: name, description, brand, and category')
            )
            return

        self.create_equipment_item(options, options.get('save_fixture', False))

    def process_batch(self, batch_file, save_fixture):
        """Process multiple items from a JSON file"""
        try:
            with open(batch_file, 'r') as f:
                items = json.load(f)
            
            created_items = []
            for item in items:
                # Convert to command options format
                options = {
                    'name': item.get('name'),
                    'description': item.get('description'),
                    'brand': item.get('brand'),
                    'model': item.get('model', ''),
                    'serial': item.get('serial', ''),
                    'purchase_date': item.get('purchase_date'),
                    'purchase_price': item.get('purchase_price'),
                    'category': item.get('category'),
                    'condition': item.get('condition', ''),
                    'notes': item.get('notes', ''),
                }
                
                created_item = self.create_equipment_item(options, False)
                if created_item:
                    created_items.append(created_item)
            
            if save_fixture and created_items:
                self.save_as_fixture(created_items)
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully processed {len(created_items)} items')
            )
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error processing batch file: {str(e)}')
            )

    def create_equipment_item(self, options, save_fixture):
        """Create a single equipment item with OpenAI pricing suggestions"""
        try:
            # First, get or create the category
            category_name = options.get('category')
            category, created = Category.objects.get_or_create(name=category_name)
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created new category: {category_name}')
                )
            
            # Use OpenAI to get pricing suggestions
            pricing_data = self.get_pricing_from_openai(
                options.get('name'),
                options.get('description'),
                options.get('brand'),
                category_name,
                options.get('purchase_price')
            )
            
            # Parse purchase date if provided
            purchase_date = None
            if options.get('purchase_date'):
                purchase_date = datetime.datetime.strptime(
                    options.get('purchase_date'), '%Y-%m-%d'
                ).date()
            
            # Create the equipment item
            equipment = Equipment(
                name=options.get('name'),
                description=options.get('description'),
                category=category,
                brand=options.get('brand'),
                model_number=options.get('model'),
                serial_number=options.get('serial'),
                purchase_date=purchase_date,
                purchase_price=Decimal(str(options.get('purchase_price'))) if options.get('purchase_price') else None,
                rental_price_daily=Decimal(str(pricing_data.get('daily_price'))),
                rental_price_weekly=Decimal(str(pricing_data.get('weekly_price'))),
                rental_price_monthly=Decimal(str(pricing_data.get('monthly_price'))),
                deposit_amount=Decimal(str(pricing_data.get('deposit_amount'))),
                status='available',
                condition=options.get('condition'),
                notes=options.get('notes')
            )
            
            equipment.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created equipment item: {equipment.name}')
            )
            
            # Display pricing info
            self.stdout.write(f'Daily Rental: ${equipment.rental_price_daily}')
            self.stdout.write(f'Weekly Rental: ${equipment.rental_price_weekly}')
            self.stdout.write(f'Monthly Rental: ${equipment.rental_price_monthly}')
            self.stdout.write(f'Deposit: ${equipment.deposit_amount}')
            
            # Save as fixture if requested
            if save_fixture:
                self.save_as_fixture([equipment])
            
            return equipment
        
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error creating equipment item: {str(e)}')
            )
            return None

    def get_pricing_from_openai(self, name, description, brand, category, purchase_price=None):
        """Use OpenAI to get suggested rental pricing and deposit amount"""
        prompt = f"""
You are a musical equipment rental specialist. Please suggest appropriate rental pricing and deposit amount for the following item:

- Name: {name}
- Description: {description}
- Brand: {brand}
- Category: {category}
{f"- Purchase Price: ${purchase_price}" if purchase_price else ""}

Based on the information above, provide the following values in numerical format only (without dollar signs or text):
1. Daily rental price
2. Weekly rental price (should be ~4x daily but with a discount)
3. Monthly rental price (should be ~4x weekly but with a discount)
4. Deposit amount (typically 20-40% of the equipment's value)

Return your response in a structured JSON format with these keys:
- daily_price
- weekly_price
- monthly_price
- deposit_amount
"""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a musical equipment pricing specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Extract the JSON from the response
            try:
                # Try to parse directly
                pricing_data = json.loads(content)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON portion
                try:
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        pricing_data = json.loads(json_match.group(0))
                    else:
                        raise ValueError("Could not extract JSON from response")
                except Exception:
                    # Fallback to defaults if parsing fails
                    self.stderr.write(self.style.WARNING('Failed to parse OpenAI response, using default values'))
                    if purchase_price:
                        default_daily = float(purchase_price) * 0.03
                    else:
                        default_daily = 50.0
                    
                    return {
                        'daily_price': default_daily,
                        'weekly_price': default_daily * 4 * 0.8,  # 20% discount
                        'monthly_price': default_daily * 4 * 4 * 0.6,  # 40% discount
                        'deposit_amount': (purchase_price * 0.3) if purchase_price else 200.0
                    }
            
            return pricing_data
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'OpenAI API error: {str(e)}'))
            # Return default values based on purchase price
            if purchase_price:
                default_daily = float(purchase_price) * 0.03
            else:
                default_daily = 50.0
                
            return {
                'daily_price': default_daily,
                'weekly_price': default_daily * 4 * 0.8,  # 20% discount
                'monthly_price': default_daily * 4 * 4 * 0.6,  # 40% discount
                'deposit_amount': (purchase_price * 0.3) if purchase_price else 200.0
            }

    def save_as_fixture(self, equipment_items):
        """Save equipment items as a fixture file"""
        try:
            # Serialize the equipment items
            serialized_data = serialize('json', equipment_items)
            
            # Determine filename with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            fixture_path = os.path.join(
                settings.BASE_DIR, 
                'inventory', 
                'fixtures', 
                f'equipment_generated_{timestamp}.json'
            )
            
            with open(fixture_path, 'w') as f:
                f.write(serialized_data)
            
            self.stdout.write(
                self.style.SUCCESS(f'Created fixture file: {fixture_path}')
            )
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error creating fixture: {str(e)}')
            )
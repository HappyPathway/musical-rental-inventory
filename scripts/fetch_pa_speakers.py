import requests
from bs4 import BeautifulSoup
import json
import uuid
from decimal import Decimal
from datetime import datetime

def fetch_pa_speakers():
    url = "https://www.sweetwater.com/c134--Powered_PA_Speakers"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        products = []
        product_cards = soup.find_all('div', class_='product-card')
        
        for idx, card in enumerate(product_cards, start=1):
            try:
                # Extract product information
                title = card.find('h2', class_='product-card__name').text.strip()
                brand = title.split()[0]
                price_elem = card.find('span', class_='product-card__price')
                price = price_elem.text.strip().replace('$', '').replace(',', '') if price_elem else '0.00'
                
                # Extract description and specs
                desc_elem = card.find('div', class_='product-card__description')
                description = desc_elem.text.strip() if desc_elem else ''
                
                # Calculate rental prices (example: daily = 3% of purchase price, weekly = 15%, monthly = 45%)
                purchase_price = Decimal(price)
                daily_rate = (purchase_price * Decimal('0.03')).quantize(Decimal('0.01'))
                weekly_rate = (purchase_price * Decimal('0.15')).quantize(Decimal('0.01'))
                monthly_rate = (purchase_price * Decimal('0.45')).quantize(Decimal('0.01'))
                deposit = (purchase_price * Decimal('0.25')).quantize(Decimal('0.01'))  # 25% deposit
                
                # Create fixture entry
                product_data = {
                    "model": "inventory.equipment",
                    "pk": idx,
                    "fields": {
                        "name": title,
                        "description": description,
                        "category": 1,  # Powered PA Speakers category
                        "brand": brand,
                        "model_number": title.replace(brand, '').strip(),
                        "serial_number": f"PA{idx:04d}-{uuid.uuid4().hex[:8]}",
                        "purchase_date": datetime.now().strftime('%Y-%m-%d'),
                        "purchase_price": str(purchase_price),
                        "rental_price_daily": str(daily_rate),
                        "rental_price_weekly": str(weekly_rate),
                        "rental_price_monthly": str(monthly_rate),
                        "deposit_amount": str(deposit),
                        "status": "available",
                        "condition": "New",
                        "notes": f"Imported from Sweetwater on {datetime.now().strftime('%Y-%m-%d')}",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                }
                products.append(product_data)
                
            except Exception as e:
                print(f"Error processing product {idx}: {e}")
                continue
        
        # Load existing category fixture
        with open('inventory/fixtures/pa_speakers.json', 'r') as f:
            fixtures = json.load(f)
        
        # Add product fixtures
        fixtures.extend(products)
        
        # Save updated fixtures
        with open('inventory/fixtures/pa_speakers.json', 'w') as f:
            json.dump(fixtures, f, indent=4)
        
        print(f"Successfully created fixtures for {len(products)} PA speakers")
        
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_pa_speakers() 
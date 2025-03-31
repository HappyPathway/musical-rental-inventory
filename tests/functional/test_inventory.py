from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from django.urls import reverse
from tests.base import BaseTestCase
from inventory.models import Category, Equipment
import uuid

User = get_user_model()


class InventoryTestCase(BaseTestCase):
    """Test cases for the inventory app functionality"""
    
    def setUp(self):
        super().setUp()
        # Create a test user
        self.test_username = 'testuser'
        self.test_password = 'testpassword123'
        self.test_email = 'test@example.com'
        
        self.user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password,
            is_staff=True  # Make the user a staff member to access admin features
        )
        
        # Create test category
        self.category = Category.objects.create(
            name=f'Test Category {uuid.uuid4().hex[:8]}',
            description='A test category for equipment'
        )
        
        # Create test equipment with unique values
        unique_id = uuid.uuid4().hex[:8]
        self.equipment = Equipment(
            name=f'Test Equipment {unique_id}',
            description='A test piece of equipment',
            brand=f'Test Brand {unique_id}',
            category=self.category,
            status='available',
            rental_price_daily=25.00,
            rental_price_weekly=150.00,
            rental_price_monthly=500.00,
            deposit_amount=100.00,
            serial_number=f'SN{unique_id}'  # Add unique serial number
        )
        self.equipment.save(skip_qr=True)
    
    def test_equipment_list_view(self):
        """Test the equipment list view loads correctly"""
        # Navigate to the equipment list page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_list')}")
        
        # Verify the page title
        self.assertIn('Equipment Inventory', self.browser.title)
        
        # Check if our test equipment is displayed
        equipment_items = self.browser.find_elements(By.CLASS_NAME, 'equipment-card')
        self.assertGreaterEqual(len(equipment_items), 1)
        
        # Verify equipment details are displayed
        self.assertIn(self.equipment.name, self.browser.page_source)
        self.assertIn(self.equipment.brand, self.browser.page_source)
        self.assertIn(str(self.equipment.rental_price_daily), self.browser.page_source)
    
    def test_equipment_detail_view(self):
        """Test the equipment detail view loads correctly"""
        # Navigate to the equipment detail page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_detail', kwargs={'pk': self.equipment.pk})}")
        
        # Verify the page title contains the equipment
        self.assertIn('Musical Equipment Inventory', self.browser.title)
        
        # Check if equipment details are displayed
        self.assertIn(self.equipment.name, self.browser.page_source)
        self.assertIn(self.equipment.brand, self.browser.page_source)
        self.assertIn(self.equipment.description, self.browser.page_source)
        self.assertIn(str(self.equipment.rental_price_daily), self.browser.page_source)
        self.assertIn(str(self.equipment.rental_price_weekly), self.browser.page_source)
        self.assertIn(str(self.equipment.rental_price_monthly), self.browser.page_source)
        self.assertIn(str(self.equipment.deposit_amount), self.browser.page_source)
    
    def test_equipment_add_requires_login(self):
        """Test that adding equipment requires login"""
        # Navigate to the add equipment page without logging in
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_add')}")
        
        # Should be redirected to login page
        self.assertIn('/accounts/login/', self.browser.current_url)
    
    def test_equipment_add(self):
        """Test adding new equipment"""
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the add equipment page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_add')}")
        
        # Fill out the form
        self.browser.find_element(By.ID, 'id_name').send_keys('New Test Equipment')
        self.browser.find_element(By.ID, 'id_brand').send_keys('New Test Brand')
        
        # Select the category
        category_select = self.browser.find_element(By.ID, 'id_category')
        for option in category_select.find_elements(By.TAG_NAME, 'option'):
            if option.text == self.category.name:
                option.click()
                break
        
        # Fill out price fields
        self.browser.find_element(By.ID, 'id_rental_price_daily').send_keys('30.00')
        self.browser.find_element(By.ID, 'id_deposit_amount').send_keys('150.00')
        
        # Fill out description
        self.browser.find_element(By.ID, 'id_description').send_keys('This is a test description for new equipment')
        
        # Scroll to the submit button to make it visible
        submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        
        # Wait a moment for scrolling to complete
        import time
        time.sleep(1)
        
        # Submit the form
        submit_button.click()
        
        # Verify redirect to detail page
        self.wait.until(EC.url_contains('/inventory/'))
        
        # Verify new equipment was added
        self.assertIn('New Test Equipment', self.browser.page_source)
        self.assertIn('New Test Brand', self.browser.page_source)
        self.assertIn('This is a test description for new equipment', self.browser.page_source)
        
    def test_equipment_search(self):
        """Test the equipment search functionality"""
        # Create another equipment item with a unique serial number and skip QR
        unique_id = uuid.uuid4().hex[:8]
        another_equipment = Equipment(
            name='Another Equipment',
            description='Another test piece of equipment',
            brand='Another Brand',
            category=self.category,
            status='available',
            rental_price_daily=35.00,
            rental_price_weekly=210.00,
            rental_price_monthly=700.00,
            deposit_amount=120.00,
            serial_number=f'SN-Another-{unique_id}'
        )
        another_equipment.save(skip_qr=True)
        
        # Navigate to the equipment list page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_list')}")
        
        # Enter search term
        search_input = self.browser.find_element(By.NAME, 'search')
        search_input.send_keys(self.equipment.name)
        
        # Submit the search form
        search_input.submit()
        
        # Wait for results to load
        self.wait_for_element(By.CLASS_NAME, 'equipment-card')
        
        # Verify that only matching equipment is shown
        self.assertIn(self.equipment.name, self.browser.page_source)
        self.assertNotIn('Another Equipment', self.browser.page_source)
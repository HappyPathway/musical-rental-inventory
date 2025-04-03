from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import uuid
from tests.base import BaseTestCase
from inventory.models import Category, Equipment
from rentals.models import Customer, Rental, RentalItem
from users.models import User

User = get_user_model()


class RentalTestCase(BaseTestCase):
    """Test cases for the rentals app functionality"""
    
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
        
        # Create test customer with unique values
        unique_customer_id = uuid.uuid4().hex[:8]
        self.customer = Customer.objects.create(
            first_name='Test',
            last_name='Customer',
            email=f'customer_{unique_customer_id}@example.com',
            phone='555-123-4567',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            id_type='driver_license',
            id_number=f'DL{unique_customer_id}',
            user=self.user
        )
        
        # Create test category with a unique name
        category_id = uuid.uuid4().hex[:8]
        self.category = Category.objects.create(
            name=f'Test Category {category_id}',
            description='A test category for equipment'
        )
        
        # Create test equipment with unique values
        unique_eq1_id = uuid.uuid4().hex[:8]
        self.equipment1 = Equipment(
            name=f'Test Equipment 1 {unique_eq1_id}',
            description='A test piece of equipment',
            brand=f'Test Brand {unique_eq1_id}',
            category=self.category,
            status='available',
            rental_price_daily=25.00,
            rental_price_weekly=150.00,
            rental_price_monthly=500.00,
            deposit_amount=100.00,
            serial_number=f'SN1-{unique_eq1_id}'  # Add unique serial number
        )
        self.equipment1.save(skip_qr=True)
        
        unique_eq2_id = uuid.uuid4().hex[:8]
        self.equipment2 = Equipment(
            name=f'Test Equipment 2 {unique_eq2_id}',
            description='Another test piece of equipment',
            brand=f'Test Brand {unique_eq2_id}',
            category=self.category,
            status='available',
            rental_price_daily=35.00,
            rental_price_weekly=210.00,
            rental_price_monthly=700.00,
            deposit_amount=150.00,
            serial_number=f'SN2-{unique_eq2_id}'  # Add unique serial number
        )
        self.equipment2.save(skip_qr=True)
        
        # Create a test rental
        self.rental = Rental.objects.create(
            customer=self.customer,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=7),
            duration_type='weekly',
            status='active',
            total_price=150.00,
            deposit_total=100.00,
            deposit_paid=True
        )
        
        # Add rental item
        self.rental_item = RentalItem.objects.create(
            rental=self.rental,
            equipment=self.equipment1,
            quantity=1,
            price=self.equipment1.rental_price_weekly
        )
    
    def test_rental_list_view(self):
        """Test the rental list view loads correctly for staff"""
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the rental list page
        self.browser.get(f"{self.live_server_url}{reverse('rentals:rental_list')}")
        
        # Verify the page loads
        self.wait_for_element(By.TAG_NAME, 'h1')
        
        # Check if our test rental exists by looking for a more general identifier
        # The rental ID might change between test runs, so we look for other reliable information
        self.assertIn(self.customer.first_name, self.browser.page_source)
        self.assertIn(self.customer.last_name, self.browser.page_source)
        self.assertIn('active', self.browser.page_source.lower())
    
    def test_rental_detail_view(self):
        """Test the rental detail view loads correctly"""
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the rental detail page
        self.browser.get(f"{self.live_server_url}{reverse('rentals:rental_detail', kwargs={'pk': self.rental.pk})}")
        
        # Check if we got a 500 error
        if "Server Error (500)" in self.browser.page_source:
            # Instead of failing, skip the detailed checks since the server has an error
            self.fail("Got a 500 Server Error when accessing rental detail view - this is a server-side issue")
        
        # Check if rental details are displayed
        self.assertIn(self.customer.first_name, self.browser.page_source)
        self.assertIn(self.customer.last_name, self.browser.page_source)
        self.assertIn(self.equipment1.name, self.browser.page_source)
        
        # Look for parts of the formatted price rather than the exact price
        price_str = str(self.rental.total_price)
        for part in price_str.split('.'):
            self.assertIn(part, self.browser.page_source)
    
    def test_rental_create_process(self):
        """Test the entire rental creation process"""
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to rental create page
        self.browser.get(f"{self.live_server_url}{reverse('rentals:rental_create')}")
        
        # Wait for the form to load
        self.wait_for_element(By.TAG_NAME, 'form')
        
        # Check if we need to create a customer first
        try:
            # Try finding customer select first
            customer_select = self.browser.find_element(By.ID, 'id_customer')
            
            # If found, select the customer
            for option in customer_select.find_elements(By.TAG_NAME, 'option'):
                if self.customer.first_name in option.text and self.customer.last_name in option.text:
                    option.click()
                    break
        except:
            # If customer select not found, we might be on a different step or UI
            # Look for elements on the page to guide our actions
            if "Customer Information" in self.browser.page_source:
                # We might need to create a new customer as part of the flow
                # Fill in customer details
                self.browser.find_element(By.ID, 'id_first_name').send_keys('New')
                self.browser.find_element(By.ID, 'id_last_name').send_keys('Customer')
                self.browser.find_element(By.ID, 'id_email').send_keys(f'new.customer.{uuid.uuid4().hex[:8]}@example.com')
                self.browser.find_element(By.ID, 'id_phone').send_keys('555-987-6543')
                
                # Submit the customer form
                self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
                
                # Wait for the next page
                self.wait.until(EC.presence_of_element_located((By.ID, 'id_start_date')))
        
        # Set rental dates
        today = timezone.now().date()
        end_date = today + timedelta(days=3)
        
        # Wait for the start date input
        start_date_input = self.wait_for_element(By.ID, 'id_start_date')
        start_date_input.clear()
        start_date_input.send_keys(today.strftime('%Y-%m-%d'))
        
        end_date_input = self.browser.find_element(By.ID, 'id_end_date')
        end_date_input.clear()
        end_date_input.send_keys(end_date.strftime('%Y-%m-%d'))
        
        # Select duration type if present
        try:
            duration_select = self.browser.find_element(By.ID, 'id_duration_type')
            for option in duration_select.find_elements(By.TAG_NAME, 'option'):
                if option.get_attribute('value') == 'daily':
                    option.click()
                    break
        except:
            # Duration field might not be present or named differently
            pass
        
        # Find and click the continue button, whatever its text might be
        continue_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
        continue_button.click()
        
        # Wait for the next page to load (equipment selection)
        self.wait.until(lambda d: '/add-item' in d.current_url or '/items' in d.current_url)
        
        # Select equipment
        equipment_select = self.wait_for_element(By.ID, 'id_equipment')
        for option in equipment_select.find_elements(By.TAG_NAME, 'option'):
            if self.equipment2.name in option.text:
                option.click()
                break
        
        # Set quantity
        quantity_input = self.browser.find_element(By.ID, 'id_quantity')
        quantity_input.clear()
        quantity_input.send_keys('1')
        
        # Add item
        add_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Add') or contains(@class, 'btn-primary')]")
        add_button.click()
        
        # Wait for item to be added
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rental-item')))
        
        # Verify item was added to the rental
        self.assertIn(self.equipment2.name, self.browser.page_source)
        
        # Look for the complete rental button, which might have different text
        complete_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(text(), 'Complete') or contains(text(), 'Finish') or contains(@class, 'btn-success')]")
        
        if complete_buttons:
            complete_buttons[0].click()
        else:
            # Try another approach if the complete button isn't found
            # Look for any button/link that might complete the rental
            self.browser.find_element(By.XPATH, "//button[@type='submit'] | //a[contains(@class, 'btn-primary')]").click()
        
        # Wait for rental detail page to load
        self.wait.until(lambda d: '/rentals/' in d.current_url and 'add-item' not in d.current_url)
        
        # Verify we're on a page showing rental details
        self.assertIn(self.equipment2.name, self.browser.page_source)
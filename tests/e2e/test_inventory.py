from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from django.urls import reverse
from tests.base import BaseTestCase
from inventory.models import Category, Equipment
import uuid
import time
from selenium.common.exceptions import TimeoutException

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


class MobileInventoryTestCase(BaseTestCase):
    """Test cases for mobile-optimized inventory features"""
    
    def setUp(self):
        super().setUp()
        # Create a test user
        self.test_username = 'mobileuser'
        self.test_password = 'mobilepass123'
        self.test_email = 'mobile@example.com'
        
        # Create user for django-allauth
        User = get_user_model()
        self.user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password,
            is_staff=True
        )
        
        # Add verified email for django-allauth
        from allauth.account.models import EmailAddress
        EmailAddress.objects.create(
            user=self.user,
            email=self.test_email,
            verified=True,
            primary=True
        )
        
        # Create test category
        self.category = Category.objects.create(
            name=f'Mobile Category {uuid.uuid4().hex[:8]}',
            description='A test category for mobile equipment testing'
        )
        
        # Create test equipment with unique values
        unique_id = uuid.uuid4().hex[:8]
        self.equipment = Equipment(
            name=f'Mobile Test Equipment {unique_id}',
            description='A test piece of equipment for mobile testing',
            brand=f'Mobile Brand {unique_id}',
            category=self.category,
            status='available',
            rental_price_daily=25.00,
            rental_price_weekly=150.00,
            rental_price_monthly=500.00,
            deposit_amount=100.00,
            serial_number=f'MOBILE-{unique_id}'
        )
        self.equipment.save(skip_qr=True)
        
        # Set mobile user agent for browser
        self.mobile_user_agent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        self.original_user_agent = self.browser.execute_script("return navigator.userAgent")
    
    def tearDown(self):
        # Reset user agent after tests
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.original_user_agent})
        super().tearDown()
    
    def set_mobile_user_agent(self):
        """Set mobile user agent to simulate mobile device"""
        self.browser.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.mobile_user_agent})
        
    def test_mobile_equipment_list_view(self):
        """Test the mobile-optimized equipment list view"""
        # Set mobile user agent
        self.set_mobile_user_agent()
        
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the equipment list page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_list')}")
        
        # Check that mobile template is used (look for mobile-specific elements)
        try:
            self.wait_for_element(By.CLASS_NAME, 'mobile-equipment-list', timeout=5)
            mobile_view_loaded = True
        except TimeoutException:
            mobile_view_loaded = False
            
        self.assertTrue(mobile_view_loaded, "Mobile optimized view not loaded")
        
        # Test search functionality
        search_input = self.browser.find_element(By.NAME, 'search')
        search_input.send_keys(self.equipment.name)
        search_input.submit()
        
        # Verify search results
        time.sleep(2)  # Allow time for search to complete
        self.assertIn(self.equipment.name, self.browser.page_source)
        
        # Test filters button exists
        filters_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Filters')]")
        self.assertIsNotNone(filters_button)
        
        # Test floating action button exists
        fab = self.browser.find_element(By.CLASS_NAME, 'floating-action-button')
        self.assertIsNotNone(fab)
    
    def test_mobile_equipment_detail_view(self):
        """Test the mobile-optimized equipment detail view with quick status updates"""
        # Set mobile user agent
        self.set_mobile_user_agent()
        
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the equipment detail page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_detail', kwargs={'pk': self.equipment.pk})}")
        
        # Check that mobile template is used
        try:
            self.wait_for_element(By.CLASS_NAME, 'mobile-equipment-detail', timeout=5)
            mobile_view_loaded = True
        except TimeoutException:
            mobile_view_loaded = False
            
        self.assertTrue(mobile_view_loaded, "Mobile optimized detail view not loaded")
        
        # Check for quick status controls
        quick_status_controls = self.browser.find_element(By.CLASS_NAME, 'quick-status-controls')
        self.assertIsNotNone(quick_status_controls)
        
        # Check for status buttons
        status_buttons = self.browser.find_elements(By.CLASS_NAME, 'quick-status-btn')
        self.assertGreaterEqual(len(status_buttons), 2, "Status buttons not found")
        
        # Test tabs exist
        tabs = self.browser.find_element(By.ID, 'equipmentTabs')
        self.assertIsNotNone(tabs)
        
        # Check maintenance tab
        maintenance_tab = self.browser.find_element(By.ID, 'maintenance-tab')
        self.assertIsNotNone(maintenance_tab)
    
    def test_mobile_scan_interface(self):
        """Test the mobile-optimized scanning interface loads correctly"""
        # Set mobile user agent
        self.set_mobile_user_agent()
        
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the scan interface
        self.browser.get(f"{self.live_server_url}{reverse('inventory:mobile_scan')}")
        
        # Check for camera container
        camera_container = self.browser.find_element(By.ID, 'camera-container')
        self.assertIsNotNone(camera_container)
        
        # Check for scanner elements
        scanner_preview = self.browser.find_element(By.ID, 'scanner-preview')
        self.assertIsNotNone(scanner_preview)
        
        # Check for manual entry option (fallback)
        manual_entry = self.browser.find_element(By.ID, 'manual-entry')
        self.assertIsNotNone(manual_entry)
        
        # Test manual entry by entering serial number
        manual_entry.send_keys(self.equipment.serial_number)
        
        # Click search button
        manual_search = self.browser.find_element(By.ID, 'manual-search')
        manual_search.click()
        
        # Should navigate to search results
        time.sleep(2)  # Allow for navigation
        self.assertIn('search=' + self.equipment.serial_number, self.browser.current_url)
        
    def test_mobile_equipment_form(self):
        """Test the mobile-optimized equipment form with camera integration"""
        # Set mobile user agent
        self.set_mobile_user_agent()
        
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the add equipment page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_add')}")
        
        # Check form loads with mobile optimizations
        form = self.browser.find_element(By.ID, 'mobile-equipment-form')
        self.assertIsNotNone(form)
        
        # Check for camera integration buttons
        scan_serial_btn = self.browser.find_element(By.ID, 'scan-serial')
        self.assertIsNotNone(scan_serial_btn)
        
        capture_photo_btn = self.browser.find_element(By.ID, 'capture-photo')
        self.assertIsNotNone(capture_photo_btn)
        
        # Fill out minimum required fields
        self.browser.find_element(By.ID, 'id_name').send_keys('Mobile Form Test Equipment')
        self.browser.find_element(By.ID, 'id_brand').send_keys('Mobile Form Test Brand')
        
        # Select the category
        category_select = self.browser.find_element(By.ID, 'id_category')
        for option in category_select.find_elements(By.TAG_NAME, 'option'):
            if option.text == self.category.name:
                option.click()
                break
        
        # Fill out price fields
        self.browser.find_element(By.ID, 'id_rental_price_daily').send_keys('30.00')
        self.browser.find_element(By.ID, 'id_rental_price_weekly').send_keys('180.00')
        self.browser.find_element(By.ID, 'id_rental_price_monthly').send_keys('600.00')
        self.browser.find_element(By.ID, 'id_deposit_amount').send_keys('150.00')
        
        # Fill out description
        self.browser.find_element(By.ID, 'id_description').send_keys('This is a test equipment added via mobile form')
        
        # Test form submission
        submit_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Save Equipment')]")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        time.sleep(1)  # Wait for scrolling
        submit_button.click()
        
        # Verify successful creation
        time.sleep(2)  # Allow for form submission
        self.assertIn('Mobile Form Test Equipment', self.browser.page_source)

    def test_quick_status_updates(self):
        """Test the quick status update functionality for mobile"""
        # Set mobile user agent
        self.set_mobile_user_agent()
        
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to the equipment detail page
        self.browser.get(f"{self.live_server_url}{reverse('inventory:equipment_detail', kwargs={'pk': self.equipment.pk})}")
        
        # Wait for page to load
        self.wait_for_element(By.CLASS_NAME, 'quick-status-btn', timeout=5)
        
        # Find the "rented" status button
        status_buttons = self.browser.find_elements(By.CLASS_NAME, 'quick-status-btn')
        rented_button = None
        
        for button in status_buttons:
            if 'Rented' in button.text:
                rented_button = button
                break
                
        self.assertIsNotNone(rented_button, "Rented status button not found")
        
        # Initial status should be "available" 
        status_badge = self.browser.find_element(By.ID, 'status-badge')
        self.assertIn('available', status_badge.get_attribute('class'))
        
        # Click the "rented" button to change status
        self.browser.execute_script("arguments[0].scrollIntoView(true);", rented_button)
        time.sleep(1)  # Wait for scrolling
        rented_button.click()
        
        # Wait for status update
        time.sleep(2)
        
        # Refresh page to verify status change persisted
        self.browser.refresh()
        
        # Wait for page to reload
        self.wait_for_element(By.ID, 'status-badge', timeout=5)
        
        # Verify status badge has changed
        status_badge = self.browser.find_element(By.ID, 'status-badge')
        self.assertIn('rented', status_badge.get_attribute('class'))
        self.assertIn('Rented', status_badge.text)
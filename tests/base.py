import os
import time
from pathlib import Path
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.test import override_settings
from django.db import connections
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from selenium.common.exceptions import (
    StaleElementReferenceException, 
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException
)

class BaseTestCase(StaticLiveServerTestCase):
    """Base test case for Selenium tests with common setup and teardown methods"""
    
    # Default review delay (seconds) to allow humans to see what's happening
    REVIEW_DELAY = 1.0
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Determine which browser to use (defaults to Chrome)
        browser = os.environ.get('BROWSER', 'chrome').lower()
        
        if browser == 'firefox':
            options = FirefoxOptions()
            options.headless = False
            service = FirefoxService(GeckoDriverManager().install())
            cls.browser = webdriver.Firefox(service=service, options=options)
        else:  # Default to Chrome
            options = ChromeOptions()
            options.headless = False
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            service = ChromeService(ChromeDriverManager().install())
            cls.browser = webdriver.Chrome(service=service, options=options)
            
        # Set window size and implicit wait time
        cls.browser.set_window_size(1280, 800)
        cls.browser.implicitly_wait(10)
        
    @classmethod
    def tearDownClass(cls):
        # Pause before closing browser
        time.sleep(cls.REVIEW_DELAY)
        cls.browser.quit()
        super().tearDownClass()
    
    def setUp(self):
        super().setUp()
        # Create test users
        self.create_test_data()
        
    def create_test_data(self):
        """Create test users and data"""
        User = get_user_model()
        
        # Create customer user if it doesn't exist
        if not User.objects.filter(username='customer').exists():
            self.customer_user = User.objects.create_user(
                username='customer',
                password='customerpass',
                email='customer@example.com',
                first_name='Test',
                last_name='Customer'
            )
        else:
            self.customer_user = User.objects.get(username='customer')
            
        # Create staff user if it doesn't exist
        if not User.objects.filter(username='staff').exists():
            self.staff_user = User.objects.create_user(
                username='staff',
                password='staffpass',
                email='staff@example.com',
                first_name='Test',
                last_name='Staff',
                is_staff=True
            )
        else:
            self.staff_user = User.objects.get(username='staff')
            
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            self.admin_user = User.objects.create_superuser(
                username='admin',
                password='adminpass',
                email='admin@example.com',
                first_name='Test',
                last_name='Admin'
            )
        else:
            self.admin_user = User.objects.get(username='admin')
            
        # Create test data (inventory, rentals, etc.)
        self.create_test_inventory()
        
    def create_test_inventory(self):
        """Create test inventory if it doesn't exist"""
        try:
            from inventory.models import Equipment, Category
            from rentals.models import Rental
            import datetime
            from django.utils import timezone
            
            # Create categories if needed
            if not Category.objects.exists():
                Category.objects.create(name="Guitars", description="Electric and acoustic guitars")
                Category.objects.create(name="Amplifiers", description="Guitar and bass amplifiers")
                Category.objects.create(name="Microphones", description="Vocal and instrument microphones")
                Category.objects.create(name="Speakers", description="PA speakers and monitors")
            
            # Create equipment if needed
            if not Equipment.objects.exists():
                guitars = Category.objects.get(name="Guitars")
                Equipment.objects.create(
                    name="Fender Stratocaster",
                    description="Classic electric guitar",
                    category=guitars,
                    status="Available",
                    condition="Excellent",
                    rental_price_daily=25.00,
                    replacement_value=1200.00
                )
                
                amps = Category.objects.get(name="Amplifiers")
                Equipment.objects.create(
                    name="Marshall JCM800",
                    description="Legendary tube amplifier",
                    category=amps,
                    status="Available",
                    condition="Good",
                    rental_price_daily=35.00,
                    replacement_value=2200.00
                )
                
                mics = Category.objects.get(name="Microphones")
                Equipment.objects.create(
                    name="Shure SM58",
                    description="Industry standard vocal microphone",
                    category=mics,
                    status="Available",
                    condition="Excellent",
                    rental_price_daily=10.00,
                    replacement_value=100.00
                )
                
            # Create a rental for the test customer
            if not Rental.objects.filter(user=self.customer_user).exists():
                start_date = timezone.now().date()
                end_date = start_date + datetime.timedelta(days=3)
                
                rental = Rental.objects.create(
                    user=self.customer_user,
                    start_date=start_date,
                    end_date=end_date,
                    status="Approved",
                    total_price=75.00
                )
                
                # Add rental items
                from rentals.models import RentalItem
                guitar = Equipment.objects.filter(category__name="Guitars").first()
                if guitar:
                    RentalItem.objects.create(
                        rental=rental,
                        equipment=guitar,
                        quantity=1
                    )
        
        except (ImportError, Exception) as e:
            # If models aren't available, skip test data creation
            print(f"Warning: Could not create test data: {str(e)}")
            pass
            
    def login(self, username, password):
        """Helper method to log in a user, handles different login form configurations"""
        # First, try to logout if already logged in
        self.browser.get(f"{self.live_server_url}/accounts/logout/")
        self.pause_for_review(1)
        
        # Go to login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        
        # Wait for page to load completely
        self.pause_for_review()
        
        # Take a screenshot for debugging
        self.take_screenshot("login-page")
        
        # Try different username field IDs (handles Django auth, django-allauth, etc.)
        username_field_ids = ["id_login", "id_username", "username"]
        password_field_ids = ["id_password", "password"]
        
        username_input = None
        password_input = None
        
        # Try to find username field
        for field_id in username_field_ids:
            try:
                username_input = self.browser.find_element(By.ID, field_id)
                break
            except NoSuchElementException:
                continue
        
        # Try to find password field
        for field_id in password_field_ids:
            try:
                password_input = self.browser.find_element(By.ID, field_id)
                break
            except NoSuchElementException:
                continue
        
        # If fields not found by ID, try by name or other attributes
        if username_input is None:
            try:
                username_input = self.browser.find_element(By.NAME, "username")
            except NoSuchElementException:
                try:
                    username_input = self.browser.find_element(By.CSS_SELECTOR, "input[type='text']")
                except NoSuchElementException:
                    pass
        
        if password_input is None:
            try:
                password_input = self.browser.find_element(By.NAME, "password")
            except NoSuchElementException:
                try:
                    password_input = self.browser.find_element(By.CSS_SELECTOR, "input[type='password']")
                except NoSuchElementException:
                    pass
        
        # If we still can't find the inputs, take screenshot and fail
        if username_input is None or password_input is None:
            self.take_screenshot("login-form-not-found")
            raise Exception("Could not find login form fields")
        
        # Clear any existing values and enter credentials
        username_input.clear()
        self.slow_type(username_input, username)
        password_input.clear()
        self.slow_type(password_input, password)
        
        # Try to find remember me checkbox if it exists
        try:
            remember_checkbox = self.browser.find_element(By.ID, "id_remember")
            if not remember_checkbox.is_selected():
                self.safe_click(remember_checkbox)
        except:
            pass
        
        # Find and click the submit button
        try:
            submit_btn = self.browser.find_element(By.XPATH, "//button[@type='submit']")
            self.safe_click(submit_btn)
        except NoSuchElementException:
            try:
                submit_btn = self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']")
                self.safe_click(submit_btn)
            except NoSuchElementException:
                self.take_screenshot("login-submit-not-found")
                raise Exception("Could not find login submit button")
        
        # Wait for redirect
        self.pause_for_review(2)
        
        # Take a screenshot after login attempt
        self.take_screenshot("after-login")
        
        # If we're still on the login page, check for error messages
        if '/login/' in self.browser.current_url:
            error_messages = self.browser.find_elements(By.CSS_SELECTOR, ".alert-error, .errorlist, .alert-danger, .invalid-feedback")
            if error_messages:
                error_text = " ".join([e.text for e in error_messages])
                raise Exception(f"Login failed with errors: {error_text}")
        
        # Verify we are logged in
        self.pause_for_review(1)
        
        # Look for logout link or username to confirm login success
        try:
            logout_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, 'logout') or contains(text(), 'Logout') or contains(text(), 'Log out')]")
            username_elements = self.browser.find_elements(By.XPATH, f"//*[contains(text(), '{username}')]")
            
            if not (len(logout_links) > 0 or len(username_elements) > 0):
                self.take_screenshot("login-verification-failed")
                print("Login verification warning: No logout link or username found, but no errors either")
        except:
            pass  # Ignore verification errors and continue
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present on the page with retry for stale elements"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                element = WebDriverWait(self.browser, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
                return element
            except StaleElementReferenceException:
                # If element became stale, retry
                time.sleep(0.5)
            except TimeoutException:
                break
        
        # One last attempt before giving up
        return self.browser.find_element(by, value)
    
    def wait_for_element_visible(self, by, value, timeout=10):
        """Wait for an element to be visible on the page with retry for stale elements"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                element = WebDriverWait(self.browser, timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
                return element
            except StaleElementReferenceException:
                # If element became stale, retry
                time.sleep(0.5)
            except TimeoutException:
                break
        
        # One last attempt before giving up
        element = self.browser.find_element(by, value)
        if element.is_displayed():
            return element
        raise TimeoutException(f"Element not visible with {by}={value} after {timeout} seconds")
    
    def wait_for_url_contains(self, text, timeout=10):
        """Wait for URL to contain specific text"""
        return WebDriverWait(self.browser, timeout).until(
            EC.url_contains(text)
        )
    
    def take_screenshot(self, name):
        """Take a screenshot for debugging purposes"""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_dir = os.path.join(settings.BASE_DIR, 'test-screenshots')
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        filename = os.path.join(screenshot_dir, f"{name}-{timestamp}.png")
        self.browser.save_screenshot(filename)
        return filename
        
    def slow_type(self, element, text):
        """Type text slowly for human review"""
        for character in text:
            element.send_keys(character)
            time.sleep(0.05)  # Short delay between characters
        time.sleep(0.5)  # Review delay after typing
        
    def pause_for_review(self, duration=None):
        """Pause for human review"""
        if duration is None:
            duration = self.REVIEW_DELAY
        time.sleep(duration)
        
    def safe_click(self, element, retries=3):
        """Click an element with retry for stale elements and handling of intercepted clicks"""
        for attempt in range(retries):
            try:
                element.click()
                return True
            except StaleElementReferenceException:
                if attempt < retries - 1:
                    time.sleep(0.5)
                else:
                    raise
            except ElementClickInterceptedException:
                try:
                    # Try to use JavaScript click as fallback
                    self.browser.execute_script("arguments[0].click();", element)
                    return True
                except:
                    if attempt < retries - 1:
                        time.sleep(0.5)
                    else:
                        raise
        return False
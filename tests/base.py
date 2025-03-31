import os
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.test import override_settings
from django.db import connections
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Use a separate test database
@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Use in-memory database for faster tests
    }
})
class BaseTestCase(StaticLiveServerTestCase):
    """Base test case for Selenium tests with common setup and teardown methods"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Determine which browser to use from environment variable or default to Chrome
        browser = os.environ.get('BROWSER', 'chrome').lower()
        
        if browser == 'firefox':
            options = FirefoxOptions()
            if os.environ.get('HEADLESS', 'true').lower() == 'true':
                options.add_argument('--headless')
            service = FirefoxService(GeckoDriverManager().install())
            cls.browser = webdriver.Firefox(service=service, options=options)
        else:  # Default to Chrome
            options = ChromeOptions()
            if os.environ.get('HEADLESS', 'true').lower() == 'true':
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            service = ChromeService(ChromeDriverManager().install())
            cls.browser = webdriver.Chrome(service=service, options=options)
            
        # Set window size and implicit wait time
        cls.browser.set_window_size(1280, 800)
        cls.browser.implicitly_wait(10)
        
        # Create a wait object to use for explicit waits
        cls.wait = WebDriverWait(cls.browser, 10)
        
    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()
    
    def setUp(self):
        super().setUp()
        # Reset sequences to prevent ID conflicts
        for connection in connections.all():
            if connection.vendor == 'sqlite':
                cursor = connection.cursor()
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='inventory_equipment';")
                cursor.close()
    
    def login(self, username, password):
        """Helper method to log in a user"""
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        self.browser.find_element("id", "id_login").send_keys(username)
        self.browser.find_element("id", "id_password").send_keys(password)
        self.browser.find_element("xpath", "//button[@type='submit']").click()
        
        # Wait for redirect to complete
        self.wait.until(
            EC.url_contains("/users/dashboard") or 
            EC.url_contains("/accounts/login")
        )
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for an element to be present on the page"""
        return WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_element_visible(self, by, value, timeout=10):
        """Wait for an element to be visible on the page"""
        return WebDriverWait(self.browser, timeout).until(
            EC.visibility_of_element_located((by, value))
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
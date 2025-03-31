from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth import get_user_model
from django.urls import reverse
from tests.base import BaseTestCase
from users.models import User

User = get_user_model()


class UserTestCase(BaseTestCase):
    """Test cases for the users app functionality"""
    
    def setUp(self):
        super().setUp()
        # Create a test user
        self.test_username = 'testuser'
        self.test_password = 'testpassword123'
        self.test_email = 'test@example.com'
        
        self.user = User.objects.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password
        )
        
        # Create a staff user
        self.staff_username = 'staffuser'
        self.staff_password = 'staffpassword123'
        self.staff_email = 'staff@example.com'
        
        self.staff = User.objects.create_user(
            username=self.staff_username,
            email=self.staff_email,
            password=self.staff_password,
            is_staff=True
        )
    
    def test_login_page(self):
        """Test that the login page loads correctly"""
        # Navigate to the login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        
        # Check that the login form elements are present
        self.assertIn('Sign In', self.browser.title)
        self.assertTrue(self.browser.find_element(By.ID, 'id_login'))
        self.assertTrue(self.browser.find_element(By.ID, 'id_password'))
        self.assertTrue(self.browser.find_element(By.XPATH, "//button[@type='submit']"))
    
    def test_successful_login(self):
        """Test successful login process"""
        # Navigate to the login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        
        # Fill in the form
        self.browser.find_element(By.ID, 'id_login').send_keys(self.test_username)
        self.browser.find_element(By.ID, 'id_password').send_keys(self.test_password)
        
        # Submit the form
        self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Wait for redirect to complete
        self.wait.until(EC.url_contains('/users/dashboard'))
        
        # Verify we're logged in
        self.assertIn('Dashboard', self.browser.title)
        self.assertIn(self.test_username, self.browser.page_source)
    
    def test_failed_login(self):
        """Test failed login with incorrect credentials"""
        # Navigate to the login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        
        # Fill in the form with incorrect password
        self.browser.find_element(By.ID, 'id_login').send_keys(self.test_username)
        self.browser.find_element(By.ID, 'id_password').send_keys('wrongpassword')
        
        # Submit the form
        self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # We should still be on the login page
        self.assertIn('Sign In', self.browser.title)
        
        # There should be an error message
        self.assertIn('The username and/or password you specified are not correct', self.browser.page_source)
    
    def test_logout(self):
        """Test logout functionality"""
        # Login first
        self.login(self.test_username, self.test_password)
        
        # Navigate to a page to confirm we're logged in
        self.browser.get(f"{self.live_server_url}{reverse('home')}")
        
        # Check if login was successful (username should be on the page)
        self.assertIn(self.test_username, self.browser.page_source)
        
        # Navigate to logout URL directly instead of clicking the link
        self.browser.get(f"{self.live_server_url}/accounts/logout/")
        
        # Check if we're redirected to login page
        self.wait.until(EC.url_contains('/accounts/login/'))
        
        # Check the page title matches the expected title for logged out users
        self.assertIn('ROKNSOUND Rental Inventory', self.browser.title)
        
        # Verify login link is present
        self.assertIn('Login', self.browser.page_source)
    
    def test_staff_access_admin(self):
        """Test that staff users can access the admin site"""
        # Login as staff user
        self.login(self.staff_username, self.staff_password)
        
        # Navigate to admin
        self.browser.get(f"{self.live_server_url}/admin/")
        
        # Should be on admin page, not redirected to login
        self.assertIn('ROKNSOUND Management Portal', self.browser.page_source)
        self.assertNotIn('login', self.browser.current_url)
    
    def test_non_staff_cannot_access_admin(self):
        """Test that non-staff users cannot access the admin site"""
        # Login as regular user
        self.login(self.test_username, self.test_password)
        
        # Navigate to admin
        self.browser.get(f"{self.live_server_url}/admin/")
        
        # Should be redirected to login
        self.assertIn('Log in', self.browser.page_source)
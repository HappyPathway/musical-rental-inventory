import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.base import BaseTestCase
from selenium.common.exceptions import StaleElementReferenceException

class AuthenticationTests(BaseTestCase):
    """Test cases for authentication workflows"""

    def test_user_registration(self):
        """Test user registration process"""
        # Access registration page from home page
        self.browser.get(f"{self.live_server_url}/")
        self.pause_for_review()
        
        # Try to find and click the register link
        try:
            # Try different ways to find the register link
            register_links = self.browser.find_elements(By.XPATH, 
                "//a[contains(@href, '/register/') or contains(text(), 'Register') or contains(text(), 'Sign up')]")
            
            if len(register_links) > 0:
                self.safe_click(register_links[0])
            else:
                # Navigate directly to registration URL
                self.browser.get(f"{self.live_server_url}/accounts/signup/")
                
        except Exception as e:
            # Navigate directly to registration URL
            self.browser.get(f"{self.live_server_url}/accounts/signup/")
        
        self.pause_for_review()
        self.take_screenshot("registration-page")
        
        # Test registration with valid data
        username = f"testuser_{int(time.time())}"
        email = f"{username}@example.com"
        password = "SecurePassword123!"
        
        # Find form fields
        try:
            # Wait for form fields to be present
            username_input = self.wait_for_element(By.ID, "id_username")
            email_input = self.wait_for_element(By.ID, "id_email")
            password1_input = self.wait_for_element(By.ID, "id_password1")
            password2_input = self.wait_for_element(By.ID, "id_password2")
            
            # Fill the form slowly for human review
            self.slow_type(username_input, username)
            self.slow_type(email_input, email)
            self.slow_type(password1_input, password)
            self.slow_type(password2_input, password)
            
            # Additional fields that might be present
            try:
                first_name_input = self.browser.find_element(By.ID, "id_first_name")
                last_name_input = self.browser.find_element(By.ID, "id_last_name")
                self.slow_type(first_name_input, "Test")
                self.slow_type(last_name_input, "User")
            except:
                pass
            
            # Terms and conditions if present
            try:
                terms_checkbox = self.browser.find_element(By.ID, "id_terms")
                if not terms_checkbox.is_selected():
                    terms_checkbox.click()
                    self.pause_for_review(0.5)
            except:
                pass
            
            # Take screenshot before submission
            self.take_screenshot("registration-form-filled")
            
            # Submit the form
            register_button = self.wait_for_element(By.XPATH, "//button[@type='submit']")
            self.safe_click(register_button)
            
            # Wait for redirect
            self.pause_for_review(3)
            
            # Take screenshot after submission
            self.take_screenshot("after-registration")
            
            # Check if still on registration page (error occurred)
            if '/signup/' in self.browser.current_url or '/register/' in self.browser.current_url:
                error_messages = self.browser.find_elements(By.CSS_SELECTOR, ".errorlist, .alert-danger, .invalid-feedback")
                if len(error_messages) > 0:
                    error_text = " ".join([e.text for e in error_messages])
                    self.fail(f"Registration failed with errors: {error_text}")
            
            # Return the created username and password for other tests
            return username, password
            
        except Exception as e:
            self.take_screenshot("registration-error")
            self.fail(f"Registration test failed: {str(e)}")

    def test_login_system(self):
        """Test login functionality"""
        # We'll use the precreated test users from BaseTestCase
        username = "customer"
        password = "customerpass"
        
        # Go to login page
        self.browser.get(f"{self.live_server_url}/accounts/login/")
        self.pause_for_review()
        self.take_screenshot("login-page")
        
        # Find form fields
        try:
            username_input = self.wait_for_element(By.ID, "id_login")
            password_input = self.wait_for_element(By.ID, "id_password")
        except:
            try:
                username_input = self.wait_for_element(By.ID, "id_username")
                password_input = self.wait_for_element(By.ID, "id_password")
            except Exception as e:
                self.take_screenshot("login-form-error")
                self.fail(f"Could not find login form fields: {str(e)}")
        
        # Clear and fill the fields
        username_input.clear()
        self.slow_type(username_input, username)
        password_input.clear()
        self.slow_type(password_input, password)
        
        # Remember me checkbox if present
        try:
            remember_checkbox = self.browser.find_element(By.ID, "id_remember")
            if not remember_checkbox.is_selected():
                remember_checkbox.click()
                self.pause_for_review(0.5)
        except:
            pass
        
        # Take screenshot before submission
        self.take_screenshot("login-form-filled")
        
        # Submit the form
        login_button = self.wait_for_element(By.XPATH, "//button[@type='submit']")
        self.safe_click(login_button)
        
        # Wait for redirect
        self.pause_for_review(3)
        
        # Take screenshot after submission
        self.take_screenshot("after-login")
        
        # Check if still on login page (error occurred)
        if '/login/' in self.browser.current_url:
            error_messages = self.browser.find_elements(By.CSS_SELECTOR, ".errorlist, .alert-danger, .invalid-feedback")
            if len(error_messages) > 0:
                error_text = " ".join([e.text for e in error_messages])
                self.fail(f"Login failed with errors: {error_text}")
        
        # Verify we're logged in by checking for logout link or username in navbar
        logout_links = self.browser.find_elements(By.XPATH, 
            "//a[contains(@href, 'logout') or contains(text(), 'Logout') or contains(text(), 'Log out')]")
        username_elements = self.browser.find_elements(By.XPATH, f"//*[contains(text(), '{username}')]")
        
        self.assertTrue(len(logout_links) > 0 or len(username_elements) > 0, 
                       f"No evidence of successful login found - no logout link or username '{username}' visible")

    def test_logout_functionality(self):
        """Test logout functionality"""
        # Login with a test user first
        username = "customer"
        password = "customerpass"
        
        # Use the login helper
        self.login(username, password)
        
        # Verify we're logged in
        self.pause_for_review()
        self.take_screenshot("before-logout")
        
        # Find and click logout link - try different approaches
        try:
            # Try direct logout link first
            logout_links = self.browser.find_elements(By.XPATH, 
                "//a[contains(@href, 'logout') or contains(text(), 'Logout') or contains(text(), 'Log out')]")
            
            if len(logout_links) > 0:
                self.safe_click(logout_links[0])
            else:
                # Look for dropdown toggle with username
                dropdown_toggles = self.browser.find_elements(By.XPATH, 
                    "//a[contains(@class, 'dropdown-toggle') or contains(@data-toggle, 'dropdown')]")
                
                if len(dropdown_toggles) > 0:
                    self.safe_click(dropdown_toggles[0])
                    self.pause_for_review()
                    
                    # Now look for logout link in dropdown
                    logout_link = self.wait_for_element(By.XPATH, 
                        "//a[contains(@href, 'logout') or contains(text(), 'Logout') or contains(text(), 'Log out')]")
                    self.safe_click(logout_link)
                else:
                    # Navigate directly to logout URL as last resort
                    self.browser.get(f"{self.live_server_url}/accounts/logout/")
        except Exception as e:
            # Direct URL as fallback
            self.browser.get(f"{self.live_server_url}/accounts/logout/")
        
        # Wait for redirect
        self.pause_for_review(3)
        
        # Take screenshot after logout
        self.take_screenshot("after-logout")
        
        # Verify we're logged out by checking for login link
        login_links = self.browser.find_elements(By.XPATH, 
            "//a[contains(@href, 'login') or contains(text(), 'Login') or contains(text(), 'Log in')]")
        self.assertGreater(len(login_links), 0, "Login link not found after logout - may still be logged in")
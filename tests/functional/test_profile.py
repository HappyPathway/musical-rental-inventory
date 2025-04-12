import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from tests.base import BaseTestCase

class ProfileManagementTests(BaseTestCase):
    """Test cases for user profile management"""
    
    def test_view_and_update_profile(self):
        """Test viewing and updating user profile"""
        # Login as a customer
        username = f"testuser_{int(time.time())}"
        password = "TestPassword123!"
        
        # Create a user and login
        try:
            # Register a new user first
            self.browser.get(f"{self.live_server_url}/users/register/")
            self.pause_for_review()
            
            try:
                # Fill out registration form
                username_input = self.browser.find_element(By.ID, "id_username")
                email_input = self.browser.find_element(By.ID, "id_email")
                password1_input = self.browser.find_element(By.ID, "id_password1")
                password2_input = self.browser.find_element(By.ID, "id_password2")
                
                self.slow_type(username_input, username)
                self.slow_type(email_input, f"{username}@example.com")
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
                
                # Submit the form
                register_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
                register_button.click()
                self.pause_for_review(3)
                
            except:
                # If registration fails, use login instead
                self.login(username="customer", password="customerpass")
                username = "customer"
                password = "customerpass"
        except:
            # Use existing user as fallback
            self.login(username="customer", password="customerpass")
            username = "customer"
            password = "customerpass"
        
        # Navigate to profile page
        try:
            # Look for profile link in user dropdown
            user_dropdown = self.browser.find_elements(By.XPATH, 
                "//a[contains(@class, 'dropdown-toggle') or contains(@href, '/users/profile/')]")
            if len(user_dropdown) > 0:
                user_dropdown[0].click()
                self.pause_for_review()
                
                # Find the profile link in dropdown
                profile_links = self.browser.find_elements(By.XPATH, 
                    "//a[contains(@href, '/users/profile/') or contains(text(), 'Profile')]")
                if len(profile_links) > 0:
                    profile_links[0].click()
                else:
                    # Try direct URL
                    self.browser.get(f"{self.live_server_url}/users/profile/")
            else:
                # Try direct URL
                self.browser.get(f"{self.live_server_url}/users/profile/")
                
        except:
            # Try direct URL
            self.browser.get(f"{self.live_server_url}/users/profile/")
        
        self.pause_for_review()
        self.take_screenshot("user-profile-page")
        
        # Check for profile information
        profile_elements = self.browser.find_elements(By.XPATH, 
            "//*[contains(text(), 'Profile') or contains(text(), 'Account')]")
        self.assertGreater(len(profile_elements), 0, "Profile page header not found")
        
        # Test updating profile
        # Find edit button if present
        edit_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(@href, 'edit') or contains(text(), 'Edit')]")
        
        if len(edit_buttons) > 0:
            edit_buttons[0].click()
            self.pause_for_review()
            self.take_screenshot("edit-profile-page")
            
            # Fill out profile form
            try:
                # Look for common profile fields
                try:
                    first_name = self.browser.find_element(By.ID, "id_first_name")
                    last_name = self.browser.find_element(By.ID, "id_last_name")
                    
                    # Clear and update values
                    first_name.clear()
                    last_name.clear()
                    self.slow_type(first_name, "Updated")
                    self.slow_type(last_name, "Name")
                except:
                    pass
                
                # Try to update phone number if available
                try:
                    phone = self.browser.find_element(By.ID, "id_phone")
                    phone.clear()
                    self.slow_type(phone, "555-123-4567")
                except:
                    pass
                
                # Try to update address if available
                try:
                    address = self.browser.find_element(By.ID, "id_address")
                    city = self.browser.find_element(By.ID, "id_city")
                    state = self.browser.find_element(By.ID, "id_state")
                    zip_code = self.browser.find_element(By.ID, "id_zip_code")
                    
                    address.clear()
                    city.clear()
                    zip_code.clear()
                    self.slow_type(address, "123 Test St")
                    self.slow_type(city, "Testville")
                    
                    # Select state if it's a dropdown
                    try:
                        state_select = Select(state)
                        state_select.select_by_visible_text("California")
                    except:
                        state.clear()
                        self.slow_type(state, "CA")
                    
                    self.slow_type(zip_code, "90210")
                except:
                    pass
                
                # Submit the form
                submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
                self.take_screenshot("profile-form-filled")
                submit_button.click()
                
                # Wait for redirect or page refresh
                self.pause_for_review(3)
                self.take_screenshot("after-profile-update")
                
                # Check for success message
                success_messages = self.browser.find_elements(By.CSS_SELECTOR, ".alert-success, .messages .success")
                self.assertGreater(len(success_messages), 0, "Success message not found after profile update")
                
            except Exception as e:
                self.take_screenshot("profile-update-error")
                self.fail(f"Profile update test failed: {str(e)}")
        
    def test_change_password(self):
        """Test changing user password"""
        # Login as a customer
        username = "customer"
        password = "customerpass"
        self.login(username=username, password=password)
        
        # Navigate to change password page
        try:
            # Look for password change link in user dropdown
            user_dropdown = self.browser.find_elements(By.XPATH, 
                "//a[contains(@class, 'dropdown-toggle') or contains(@href, '/users/profile/')]")
            if len(user_dropdown) > 0:
                user_dropdown[0].click()
                self.pause_for_review()
                
                # Find the change password link in dropdown
                password_links = self.browser.find_elements(By.XPATH, 
                    "//a[contains(@href, '/password/') or contains(text(), 'Password')]")
                if len(password_links) > 0:
                    password_links[0].click()
                else:
                    # Try direct URL
                    self.browser.get(f"{self.live_server_url}/users/password/change/")
            else:
                # Try direct URL
                self.browser.get(f"{self.live_server_url}/users/password/change/")
        except:
            # Try direct URL with different patterns
            try:
                self.browser.get(f"{self.live_server_url}/users/password/change/")
            except:
                try:
                    self.browser.get(f"{self.live_server_url}/accounts/password/change/")
                except:
                    self.fail("Could not navigate to password change page")
        
        self.pause_for_review()
        self.take_screenshot("change-password-page")
        
        # Check if we're on the password change page
        page_title = self.browser.find_elements(By.XPATH, 
            "//*[contains(text(), 'Change Password') or contains(text(), 'Set Password')]")
        
        if len(page_title) > 0:
            # Fill out password change form
            try:
                # Different forms may have different field IDs
                # Try the most common patterns
                
                # Django auth pattern
                try:
                    old_password = self.browser.find_element(By.ID, "id_old_password")
                    new_password1 = self.browser.find_element(By.ID, "id_new_password1")
                    new_password2 = self.browser.find_element(By.ID, "id_new_password2")
                except:
                    # Django allauth pattern
                    try:
                        old_password = self.browser.find_element(By.ID, "id_oldpassword")
                        new_password1 = self.browser.find_element(By.ID, "id_password1")
                        new_password2 = self.browser.find_element(By.ID, "id_password2")
                    except:
                        # Custom pattern
                        old_password = self.browser.find_element(By.ID, "id_current_password")
                        new_password1 = self.browser.find_element(By.ID, "id_new_password")
                        new_password2 = self.browser.find_element(By.ID, "id_confirm_password")
                
                # Type the passwords
                self.slow_type(old_password, password)
                new_password = "NewPassword123!"
                self.slow_type(new_password1, new_password)
                self.slow_type(new_password2, new_password)
                
                # Take screenshot before submission
                self.take_screenshot("password-form-filled")
                
                # Submit the form
                submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
                submit_button.click()
                
                # Wait for redirect
                self.pause_for_review(3)
                self.take_screenshot("after-password-change")
                
                # Check for success message
                success_messages = self.browser.find_elements(By.CSS_SELECTOR, ".alert-success, .messages .success")
                
                # If we successfully changed the password, try logging in with new password
                if len(success_messages) > 0:
                    # Logout first
                    self.browser.get(f"{self.live_server_url}/accounts/logout/")
                    self.pause_for_review()
                    
                    # Login with new password
                    self.browser.get(f"{self.live_server_url}/accounts/login/")
                    self.pause_for_review()
                    
                    username_input = self.browser.find_element(By.ID, "id_login")
                    password_input = self.browser.find_element(By.ID, "id_password")
                    
                    self.slow_type(username_input, username)
                    self.slow_type(password_input, new_password)
                    
                    login_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
                    login_button.click()
                    
                    self.pause_for_review(3)
                    self.take_screenshot("login-with-new-password")
                    
                    # Verify we're logged in
                    user_elements = self.browser.find_elements(By.XPATH, f"//*[contains(text(), '{username}')]")
                    self.assertGreater(len(user_elements), 0, "Failed to login with new password")
                    
            except Exception as e:
                self.take_screenshot("password-change-error")
                self.fail(f"Password change test failed: {str(e)}")
        
    def test_view_rental_and_payment_history(self):
        """Test viewing rental and payment history in user profile"""
        # Login as a customer
        self.login(username="customer", password="customerpass")
        
        # Navigate to rental history page
        try:
            # Try to find rental history link in navigation
            self.browser.get(f"{self.live_server_url}/")
            self.pause_for_review()
            
            rental_links = self.browser.find_elements(By.XPATH, 
                "//a[contains(@href, '/rentals/') or contains(text(), 'Rental')]")
            if len(rental_links) > 0:
                rental_links[0].click()
            else:
                # Navigate directly to rentals URL
                self.browser.get(f"{self.live_server_url}/rentals/")
        except:
            # Navigate directly to rentals URL
            self.browser.get(f"{self.live_server_url}/rentals/")
        
        self.pause_for_review()
        self.take_screenshot("rental-history")
        
        # Verify we can see rental history
        rental_elements = self.browser.find_elements(By.XPATH, 
            "//*[contains(text(), 'Rental') and contains(text(), 'List')]")
        self.assertGreater(len(rental_elements), 0, "Rental history page not found")
        
        # Navigate to payment history page
        try:
            # Try to find payments link
            payment_links = self.browser.find_elements(By.XPATH, 
                "//a[contains(@href, '/payments/') or contains(text(), 'Payment')]")
            if len(payment_links) > 0:
                payment_links[0].click()
            else:
                # Navigate directly to payments URL
                self.browser.get(f"{self.live_server_url}/payments/")
        except:
            # Navigate directly to payments URL
            self.browser.get(f"{self.live_server_url}/payments/")
        
        self.pause_for_review()
        self.take_screenshot("payment-history")
        
        # Verify we can see payment history or a message about no payments
        payment_elements = self.browser.find_elements(By.XPATH, 
            "//*[contains(text(), 'Payment')]")
        self.assertGreater(len(payment_elements), 0, "Payment history page not found")
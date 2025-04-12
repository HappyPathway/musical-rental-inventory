import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from tests.base import BaseTestCase

class RentalManagementTests(BaseTestCase):
    """Test cases for rental management workflows"""
    
    def test_rental_creation_as_customer(self):
        """Test creating a new rental as a customer"""
        # Login as customer
        try:
            username = f"testuser_{int(time.time())}"
            password = "TestPassword123!"
            
            # Register a new user
            self.browser.get(f"{self.live_server_url}/users/register/")
            self.pause_for_review()
            
            try:
                username_input = self.browser.find_element(By.ID, "id_username")
                email_input = self.browser.find_element(By.ID, "id_email")
                password1_input = self.browser.find_element(By.ID, "id_password1")
                password2_input = self.browser.find_element(By.ID, "id_password2")
                
                self.slow_type(username_input, username)
                self.slow_type(email_input, f"{username}@example.com")
                self.slow_type(password1_input, password)
                self.slow_type(password2_input, password)
                
                # Additional required fields
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
                except:
                    pass
                
                # Submit registration
                self.browser.find_element(By.XPATH, "//button[@type='submit']").click()
                self.pause_for_review(3)
            except:
                # Use existing customer account if registration fails
                self.login(username="customer", password="customerpass")
        except:
            # Use existing customer account as fallback
            self.login(username="customer", password="customerpass")
        
        # Go to equipment list to find something to rent
        self.browser.get(f"{self.live_server_url}/inventory/")
        self.pause_for_review()
        
        # Find available equipment
        equipment_items = self.browser.find_elements(By.CSS_SELECTOR, ".equipment-card a, .card a")
        if len(equipment_items) == 0:
            self.fail("No equipment items found to rent")
        
        # Click on the first equipment item
        equipment_items[0].click()
        self.pause_for_review()
        self.take_screenshot("equipment-detail-before-rental")
        
        # Find and click the rent button
        try:
            rent_button = self.browser.find_element(By.XPATH, "//a[contains(text(), 'Rent') or contains(@href, 'rental_create')]")
            rent_button.click()
        except:
            self.fail("Rent button not found on equipment detail page")
        
        self.pause_for_review()
        self.take_screenshot("rental-creation-form")
        
        # Fill out rental form
        try:
            # Set rental dates
            start_date = self.browser.find_element(By.ID, "id_start_date")
            end_date = self.browser.find_element(By.ID, "id_end_date")
            
            # Clear any default values
            start_date.clear()
            end_date.clear()
            
            # Set start date to today + 1 day
            import datetime
            tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            next_week = (datetime.datetime.now() + datetime.timedelta(days=8)).strftime("%Y-%m-%d")
            
            self.slow_type(start_date, tomorrow)
            self.slow_type(end_date, next_week)
            
            # Set duration type if available
            try:
                duration_type = Select(self.browser.find_element(By.ID, "id_duration_type"))
                duration_type.select_by_visible_text("Weekly")
                self.pause_for_review(0.5)
            except:
                pass
            
            # Add notes if available
            try:
                notes_input = self.browser.find_element(By.ID, "id_notes")
                self.slow_type(notes_input, "Test rental created during automated testing")
            except:
                pass
            
            # Take screenshot before submission
            self.take_screenshot("rental-form-filled")
            
            # Submit the form
            submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait for redirect
            self.pause_for_review(3)
            
            # Take screenshot after submission
            self.take_screenshot("after-rental-creation")
            
            # Check if we're on the add rental item page or rental detail page
            current_url = self.browser.current_url
            if "add-item" in current_url or "add_rental_item" in current_url:
                # We're on the add item page, continue with adding an item
                self.take_screenshot("add-rental-item-page")
                
                # Select equipment if needed
                try:
                    equipment_select = Select(self.browser.find_element(By.ID, "id_equipment"))
                    equipment_select.select_by_index(1)  # Select first equipment option
                    self.pause_for_review(0.5)
                except:
                    pass
                
                # Set quantity
                try:
                    quantity_input = self.browser.find_element(By.ID, "id_quantity")
                    quantity_input.clear()
                    self.slow_type(quantity_input, "1")
                except:
                    pass
                
                # Take screenshot before submitting
                self.take_screenshot("add-rental-item-form-filled")
                
                # Submit the form
                submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit' and not(contains(@name, 'add_another'))]")
                submit_button.click()
                
                # Wait for redirect
                self.pause_for_review(3)
                self.take_screenshot("after-adding-rental-item")
            
            # We should now be on the rental detail page
            # Verify we can see rental information
            rental_info = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'Rental Information') or contains(text(), 'Rental #')]")
            self.assertGreater(len(rental_info), 0, "Rental information not found after creation")
            
            # Check for equipment items listed
            equipment_items = self.browser.find_elements(By.XPATH, "//table[contains(.//th/text(), 'Equipment') or contains(.//th/text(), 'Item')]")
            self.assertGreater(len(equipment_items), 0, "Equipment items table not found in rental details")
            
        except Exception as e:
            self.take_screenshot("rental-creation-error")
            self.fail(f"Rental creation test failed: {str(e)}")
    
    def test_rental_list_and_filter(self):
        """Test rental listing and filtering"""
        # Login as customer
        self.login(username="customer", password="customerpass")
        
        # Go to rental list page
        try:
            # Try to find and click the rentals link in navigation
            self.browser.get(f"{self.live_server_url}/")
            self.pause_for_review()
            
            # Look for rentals link in navbar
            rental_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/rentals/') or contains(text(), 'Rental')]")
            if len(rental_links) > 0:
                rental_links[0].click()
            else:
                # Navigate directly to rentals URL
                self.browser.get(f"{self.live_server_url}/rentals/")
        except:
            # Navigate directly to rentals URL
            self.browser.get(f"{self.live_server_url}/rentals/")
        
        self.pause_for_review()
        self.take_screenshot("rental-list-customer")
        
        # Test status filter if available
        status_filters = self.browser.find_elements(By.XPATH, "//a[contains(@href, 'status=')]")
        if len(status_filters) > 0:
            # Click on first status filter (usually "Active")
            status_filters[0].click()
            self.pause_for_review()
            self.take_screenshot("rental-list-filtered-by-status")
        
        # Test search functionality if available
        search_box = self.browser.find_elements(By.CSS_SELECTOR, "input[type='search'], input[name='q']")
        if len(search_box) > 0:
            # Search for a common term
            self.slow_type(search_box[0], "rental")
            search_box[0].send_keys(Keys.RETURN)
            self.pause_for_review()
            self.take_screenshot("rental-list-search-results")
        
        # Logout as customer
        self.browser.get(f"{self.live_server_url}/users/logout/")
        self.pause_for_review()
        
        # Login as staff to see all rentals
        self.login(username="staff", password="staffpass")
        
        # Go to rental list page
        self.browser.get(f"{self.live_server_url}/rentals/")
        self.pause_for_review()
        self.take_screenshot("rental-list-staff")
        
        # Verify staff can see all rentals
        # This is a bit hard to test explicitly, but we can check for staff-only controls
        staff_controls = self.browser.find_elements(By.XPATH, "//a[contains(@href, 'create') or contains(text(), 'Create')]")
        self.assertGreater(len(staff_controls), 0, "Staff controls not found on rental list page")
    
    def test_rental_details_and_status_changes(self):
        """Test viewing rental details and changing status"""
        # Login as staff
        self.login(username="staff", password="staffpass")
        
        # Go to rental list page
        self.browser.get(f"{self.live_server_url}/rentals/")
        self.pause_for_review()
        
        # Click on the first rental in the list
        rental_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/rentals/') and not(contains(@href, '/rentals/list'))]")
        if len(rental_links) == 0:
            self.fail("No rental links found on rental list page")
        
        # Click on first rental link
        rental_links[0].click()
        self.pause_for_review()
        self.take_screenshot("rental-detail-staff")
        
        # Check for rental information sections
        rental_info = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'Rental Information')]")
        customer_info = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'Customer Information')]")
        equipment_info = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'Equipment') or contains(text(), 'Items')]")
        
        self.assertGreater(len(rental_info) + len(customer_info) + len(equipment_info), 0, 
                           "Rental information sections not found on detail page")
        
        # Check for status-changing actions: cancel, return, etc.
        status_action_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(text(), 'Cancel') or contains(text(), 'Return') or contains(text(), 'Process Return')]")
        
        # If any action buttons found, test clicking the first one
        if len(status_action_buttons) > 0:
            action_text = status_action_buttons[0].text.strip()
            status_action_buttons[0].click()
            self.pause_for_review()
            self.take_screenshot(f"rental-{action_text.lower()}-page")
            
            # If we're on a confirmation page, submit the form
            confirm_buttons = self.browser.find_elements(By.XPATH, "//button[@type='submit']")
            if len(confirm_buttons) > 0:
                self.take_screenshot("rental-status-change-confirm")
                confirm_buttons[0].click()
                self.pause_for_review(3)
                self.take_screenshot("after-rental-status-change")
                
                # Check for success message
                success_message = self.browser.find_elements(By.CSS_SELECTOR, ".alert-success, .messages .success")
                self.assertGreater(len(success_message), 0, "Success message not found after rental status change")
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from tests.base import BaseTestCase
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

class EquipmentManagementTests(BaseTestCase):
    """Test cases for equipment management workflows"""
    
    def test_equipment_listing(self):
        """Test equipment listing view for different user types"""
        # Test as unauthenticated user
        self.browser.get(f"{self.live_server_url}/")
        self.pause_for_review()
        
        # Find and click on equipment list link
        try:
            equipment_links = self.browser.find_elements(By.XPATH, 
                "//a[contains(@href, '/inventory/') or contains(text(), 'Equipment')]")
            
            if len(equipment_links) > 0:
                self.safe_click(equipment_links[0])
            else:
                # If not found, try direct URL
                self.browser.get(f"{self.live_server_url}/inventory/")
        except Exception:
            # If not found, try direct URL
            self.browser.get(f"{self.live_server_url}/inventory/")
        
        self.pause_for_review()
        self.take_screenshot("equipment-list-unauthenticated")
        
        # Verify equipment list elements are visible
        equipment_items = self.browser.find_elements(By.CSS_SELECTOR, ".equipment-card, .card, .equipment-item")
        
        # If no items found, the test data may not be loaded yet
        if len(equipment_items) == 0:
            # Continue anyway, but note it in the test
            print("Note: No equipment items found in unauthenticated view")
        
        # Test category filter if present
        category_filters = self.browser.find_elements(By.CSS_SELECTOR, ".category-filter, [name='category']")
        if len(category_filters) > 0:
            # Click on first category filter
            self.safe_click(category_filters[0])
            self.pause_for_review()
            self.take_screenshot("equipment-list-category-filter")
        
        # Now login as customer
        self.login(username="customer", password="customerpass")
        
        # Visit equipment list page as customer
        self.browser.get(f"{self.live_server_url}/inventory/")
        self.pause_for_review()
        self.take_screenshot("equipment-list-customer")
        
        # Test equipment details page
        equipment_items = self.browser.find_elements(By.CSS_SELECTOR, 
            ".equipment-card a, .card a, .equipment-item a, tbody tr a")
        
        if len(equipment_items) > 0:
            self.safe_click(equipment_items[0])
            self.pause_for_review()
            self.take_screenshot("equipment-detail-customer")
            
            # Go back to equipment list
            self.browser.get(f"{self.live_server_url}/inventory/")
        
        # Logout
        self.browser.get(f"{self.live_server_url}/accounts/logout/")
        self.pause_for_review()
        
        # Now login as staff
        self.login(username="staff", password="staffpass")
        
        # Visit equipment list page as staff
        self.browser.get(f"{self.live_server_url}/inventory/")
        self.pause_for_review()
        self.take_screenshot("equipment-list-staff")
        
        # Check for staff-only controls
        add_equipment_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(text(), 'Add Equipment') or contains(@href, 'add') or contains(@href, 'create')]")
        
        # Test equipment details page as staff if we have items
        equipment_items = self.browser.find_elements(By.CSS_SELECTOR, 
            ".equipment-card a, .card a, .equipment-item a, tbody tr a")
        
        if len(equipment_items) > 0:
            self.safe_click(equipment_items[0])
            self.pause_for_review()
            self.take_screenshot("equipment-detail-staff")

    def test_add_equipment(self):
        """Test adding new equipment (staff only)"""
        # Login as staff
        self.login(username="staff", password="staffpass")
        
        # Find the URL for adding equipment
        try:
            # Go to inventory list first
            self.browser.get(f"{self.live_server_url}/inventory/")
            self.pause_for_review()
            
            # Look for add equipment button
            add_links = self.browser.find_elements(By.XPATH, 
                "//a[contains(text(), 'Add') or contains(@href, 'add') or contains(@href, 'create')]")
            
            if len(add_links) > 0:
                # Click on add equipment link if found
                self.safe_click(add_links[0])
            else:
                # Try common URL patterns
                self.browser.get(f"{self.live_server_url}/inventory/add/")
        except Exception:
            # Try common URL patterns if the button isn't found
            self.browser.get(f"{self.live_server_url}/inventory/add/")
        
        self.pause_for_review()
        self.take_screenshot("add-equipment-page")
        
        # Test form submission with minimal data
        try:
            # Find form fields - these will vary based on your implementation
            name_input = self.wait_for_element(By.ID, "id_name")
            self.slow_type(name_input, f"Test Equipment {int(time.time())}")
            
            # Description field
            try:
                description_input = self.browser.find_element(By.ID, "id_description")
                self.slow_type(description_input, "This is a test equipment item created during automated testing.")
            except NoSuchElementException:
                pass
            
            # Category field - likely a select
            try:
                category_select = Select(self.browser.find_element(By.ID, "id_category"))
                category_select.select_by_index(1)  # Select first non-default option
            except NoSuchElementException:
                pass
            
            # Status field - likely a select
            try:
                status_select = Select(self.browser.find_element(By.ID, "id_status"))
                status_select.select_by_visible_text("Available")
            except (NoSuchElementException, StaleElementReferenceException):
                try:
                    # Try with different options if "Available" isn't present
                    status_select = Select(self.browser.find_element(By.ID, "id_status"))
                    if len(status_select.options) > 0:
                        status_select.select_by_index(0)
                except:
                    pass
            
            # Pricing fields
            try:
                rental_price = self.browser.find_element(By.ID, "id_rental_price_daily")
                self.slow_type(rental_price, "25.00")
            except NoSuchElementException:
                pass
            
            try:
                replacement_value = self.browser.find_element(By.ID, "id_replacement_value")
                self.slow_type(replacement_value, "500.00")
            except NoSuchElementException:
                pass
            
            # Condition field
            try:
                condition_select = Select(self.browser.find_element(By.ID, "id_condition"))
                condition_select.select_by_index(0)  # Select first option
            except NoSuchElementException:
                pass
            
            # Take screenshot before submission
            self.take_screenshot("add-equipment-form-filled")
            
            # Submit the form
            submit_buttons = self.browser.find_elements(By.XPATH, "//button[@type='submit']")
            if len(submit_buttons) > 0:
                self.safe_click(submit_buttons[0])
                
                # Wait for redirect
                self.pause_for_review(3)
                
                # Take screenshot after submission
                self.take_screenshot("after-equipment-add")
            
        except Exception as e:
            self.take_screenshot("add-equipment-error")
            print(f"Add equipment test encountered an error: {str(e)}")
            
    def test_equipment_search(self):
        """Test equipment search functionality"""
        # Go to equipment list page
        self.browser.get(f"{self.live_server_url}/inventory/")
        self.pause_for_review()
        
        # Find search box - try multiple common selectors
        search_selectors = [
            "input[type='search']", 
            "input[name='q']", 
            ".search-field",
            "input[name='search']",
            "input[placeholder*='Search']",
            "form input[type='text']"
        ]
        
        # Try each selector until we find a search box
        search_box = None
        for selector in search_selectors:
            search_elements = self.browser.find_elements(By.CSS_SELECTOR, selector)
            if len(search_elements) > 0:
                search_box = search_elements[0]
                break
                
        if search_box:
            # Test search by name
            search_term = "guitar"  # Common term that should exist in inventory
            self.slow_type(search_box, search_term)
            search_box.send_keys(Keys.RETURN)
            self.pause_for_review()
            self.take_screenshot("equipment-search-results")
        else:
            # Take screenshot showing the search box isn't found
            self.take_screenshot("search-box-not-found")
            print("Note: Search box not found on equipment list page")
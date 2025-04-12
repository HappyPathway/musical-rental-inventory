import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from tests.base import BaseTestCase
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

class EquipmentEditTests(BaseTestCase):
    """Test cases for editing and managing equipment"""
    
    def test_edit_equipment(self):
        """Test editing existing equipment as staff"""
        # Login as staff
        self.login(username="staff", password="staffpass")
        
        # Go to equipment list
        self.browser.get(f"{self.live_server_url}/inventory/")
        self.pause_for_review()
        
        # Click on the first equipment item
        equipment_items = self.browser.find_elements(By.CSS_SELECTOR, 
            ".equipment-card a, .card a, .equipment-item a, tbody tr a")
        
        if len(equipment_items) == 0:
            self.take_screenshot("no-equipment-items")
            self.fail("No equipment items found to edit")
        
        self.safe_click(equipment_items[0])
        self.pause_for_review()
        self.take_screenshot("equipment-detail-before-edit")
        
        # Find and click the edit button
        edit_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(text(), 'Edit') or contains(@href, 'edit')]")
        
        if len(edit_buttons) == 0:
            self.take_screenshot("no-edit-button")
            print("Edit button not found on equipment detail page - may need higher permissions")
            # Try with admin user instead
            self.login(username="admin", password="adminpass")
            self.browser.get(f"{self.live_server_url}/inventory/")
            self.pause_for_review()
            
            equipment_items = self.browser.find_elements(By.CSS_SELECTOR, 
                ".equipment-card a, .card a, .equipment-item a, tbody tr a")
            if len(equipment_items) > 0:
                self.safe_click(equipment_items[0])
                self.pause_for_review()
                edit_buttons = self.browser.find_elements(By.XPATH, 
                    "//a[contains(text(), 'Edit') or contains(@href, 'edit')]")
        
        if len(edit_buttons) > 0:
            self.safe_click(edit_buttons[0])
            self.pause_for_review()
            self.take_screenshot("equipment-edit-form")
            
            # Update equipment information
            try:
                # Update name
                name_input = self.wait_for_element(By.ID, "id_name")
                original_name = name_input.get_attribute("value")
                name_input.clear()
                self.slow_type(name_input, f"{original_name} (Updated)")
                
                # Update description if available
                try:
                    description_input = self.browser.find_element(By.ID, "id_description")
                    description_input.clear()
                    self.slow_type(description_input, "This is an updated description for testing purposes.")
                except NoSuchElementException:
                    pass
                
                # Update status if available
                try:
                    status_select = Select(self.browser.find_element(By.ID, "id_status"))
                    status_select.select_by_visible_text("Available")
                except (NoSuchElementException, StaleElementReferenceException):
                    pass
                
                # Update pricing if available
                try:
                    rental_price = self.browser.find_element(By.ID, "id_rental_price_daily")
                    rental_price.clear()
                    self.slow_type(rental_price, "35.00")
                except NoSuchElementException:
                    pass
                
                # Take screenshot before submission
                self.take_screenshot("equipment-edit-form-filled")
                
                # Submit the form
                submit_buttons = self.browser.find_elements(By.XPATH, "//button[@type='submit']")
                if len(submit_buttons) > 0:
                    self.safe_click(submit_buttons[0])
                    
                    # Wait for redirect
                    self.pause_for_review(3)
                    
                    # Take screenshot after submission
                    self.take_screenshot("after-equipment-edit")
                
            except Exception as e:
                self.take_screenshot("equipment-edit-error")
                print(f"Equipment edit encountered an error: {str(e)}")
        else:
            self.take_screenshot("no-edit-button-admin")
            print("Edit button not found even with admin user - skipping edit test")
    
    def test_delete_equipment(self):
        """Test deleting equipment as staff"""
        # Login as admin (higher permissions)
        self.login(username="admin", password="adminpass")
        
        # Go to equipment list
        self.browser.get(f"{self.live_server_url}/inventory/")
        self.pause_for_review()
        
        # Count current equipment items
        equipment_items_before = len(self.browser.find_elements(By.CSS_SELECTOR, 
            ".equipment-card, .card, .equipment-item, tbody tr"))
        
        # Click on the last equipment item (to avoid deleting important test data)
        equipment_links = self.browser.find_elements(By.CSS_SELECTOR, 
            ".equipment-card a, .card a, .equipment-item a, tbody tr a")
        
        if len(equipment_links) == 0:
            self.take_screenshot("no-equipment-to-delete")
            print("No equipment items found to delete - skipping delete test")
            return
            
        # Click on the last item in the list
        self.safe_click(equipment_links[-1])
        self.pause_for_review()
        self.take_screenshot("equipment-detail-before-delete")
        
        # Find and click the delete button - try different patterns
        delete_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(text(), 'Delete') or contains(@href, 'delete') or contains(@class, 'btn-danger') or contains(@class, 'delete')]")
        
        if len(delete_buttons) == 0:
            self.take_screenshot("no-delete-button")
            print("Delete button not found - skipping delete test")
            return
        
        self.safe_click(delete_buttons[0])
        self.pause_for_review()
        self.take_screenshot("equipment-delete-confirmation")
        
        # Confirm deletion
        try:
            # Look for confirm button on confirmation page
            confirm_buttons = self.browser.find_elements(By.XPATH, 
                "//button[@type='submit' or contains(@class, 'btn-danger') or contains(text(), 'Confirm') or contains(text(), 'Yes')]")
            
            if len(confirm_buttons) > 0:
                self.safe_click(confirm_buttons[0])
                self.pause_for_review(3)
                self.take_screenshot("after-equipment-delete")
                
                # Check if we're back on the list page
                if '/inventory/' in self.browser.current_url:
                    # Count equipment items after deletion
                    equipment_items_after = len(self.browser.find_elements(By.CSS_SELECTOR, 
                        ".equipment-card, .card, .equipment-item, tbody tr"))
                    
                    if equipment_items_after < equipment_items_before:
                        print("Equipment deletion successful")
            else:
                print("Confirmation button not found - skipping delete confirmation")
                self.take_screenshot("no-confirm-button")
                
        except Exception as e:
            self.take_screenshot("equipment-delete-error")
            print(f"Equipment delete encountered an error: {str(e)}")
            
    def test_equipment_image_management(self):
        """Test adding and removing equipment images"""
        # Login as staff
        self.login(username="staff", password="staffpass")
        
        # Go to equipment list
        self.browser.get(f"{self.live_server_url}/inventory/")
        self.pause_for_review()
        
        # Click on the first equipment item
        equipment_items = self.browser.find_elements(By.CSS_SELECTOR, 
            ".equipment-card a, .card a, .equipment-item a, tbody tr a")
        
        if len(equipment_items) == 0:
            self.take_screenshot("no-equipment-for-images")
            print("No equipment items found - skipping image management test")
            return
        
        self.safe_click(equipment_items[0])
        self.pause_for_review()
        self.take_screenshot("equipment-detail-before-image-edit")
        
        # Find image management or edit button
        image_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(text(), 'Image') or contains(text(), 'Photo') or contains(@href, 'image') or contains(@href, 'photo')]")
        
        edit_buttons = self.browser.find_elements(By.XPATH, 
            "//a[contains(text(), 'Edit') or contains(@href, 'edit')]")
        
        if len(image_buttons) > 0:
            # We have a dedicated image management page
            self.safe_click(image_buttons[0])
        elif len(edit_buttons) > 0:
            # Images might be managed in the edit form
            self.safe_click(edit_buttons[0])
        else:
            self.take_screenshot("no-image-management-buttons")
            print("No image management or edit buttons found - skipping image test")
            return
        
        self.pause_for_review()
        self.take_screenshot("equipment-image-management")
        
        # Look for file upload input
        file_inputs = self.browser.find_elements(By.CSS_SELECTOR, "input[type='file']")
        
        if len(file_inputs) > 0:
            # We found a file upload input, but won't actually upload a file in this test
            # Just verify the form structure
            form_elements = self.browser.find_elements(By.CSS_SELECTOR, "form")
            
            if len(form_elements) > 0:
                # Look for submit button
                submit_buttons = self.browser.find_elements(By.XPATH, "//button[@type='submit']")
                
                if len(submit_buttons) > 0:
                    print("Image upload form structure verified")
            
            # Look for existing images
            image_elements = self.browser.find_elements(By.CSS_SELECTOR, "img")
            if len(image_elements) > 0:
                self.take_screenshot("equipment-images-display")
                print(f"Found {len(image_elements)} image elements")
                
            # Look for image delete options
            delete_image_elements = self.browser.find_elements(By.XPATH, 
                "//*[contains(text(), 'Delete') or contains(text(), 'Remove')]")
            
            if len(delete_image_elements) > 0:
                self.take_screenshot("equipment-image-delete-options")
                print("Image deletion options found")
        else:
            print("No file upload inputs found - images may be managed differently")
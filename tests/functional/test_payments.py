import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from tests.base import BaseTestCase

class PaymentProcessingTests(BaseTestCase):
    """Test cases for payment processing workflows"""

    def test_payment_creation(self):
        """Test creating a new payment for a rental"""
        # Login as customer
        self.login(username="customer", password="customerpass")
        
        # First, find an existing rental to pay for
        self.browser.get(f"{self.live_server_url}/rentals/")
        self.pause_for_review()
        
        # Click on the first rental in the list
        rental_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/rentals/') and not(contains(@href, '/rentals/list'))]")
        if len(rental_links) == 0:
            self.fail("No rental links found on rental list page")
        
        # Click on first rental link
        rental_links[0].click()
        self.pause_for_review()
        self.take_screenshot("rental-detail-before-payment")
        
        # Look for make payment button
        payment_buttons = self.browser.find_elements(By.XPATH, "//a[contains(text(), 'Make Payment') or contains(@href, 'payment')]")
        if len(payment_buttons) == 0:
            self.fail("No payment button found on rental detail page")
        
        # Click on payment button
        payment_buttons[0].click()
        self.pause_for_review()
        self.take_screenshot("payment-creation-form")
        
        # Fill out payment form
        try:
            # Amount field
            amount_input = self.browser.find_element(By.ID, "id_amount")
            amount_input.clear()
            self.slow_type(amount_input, "50.00")  # Sample payment amount
            
            # Payment method selection
            try:
                payment_method_select = Select(self.browser.find_element(By.ID, "id_payment_method"))
                # Select the first non-default option (might be PayPal, Credit Card, etc.)
                payment_method_select.select_by_index(1)
                self.pause_for_review(0.5)
            except:
                pass
            
            # Payment type selection if available
            try:
                payment_type_select = Select(self.browser.find_element(By.ID, "id_payment_type"))
                # Usually first option is "Rental Payment" or similar
                payment_type_select.select_by_index(0)
                self.pause_for_review(0.5)
            except:
                pass
            
            # Notes field if available
            try:
                notes_input = self.browser.find_element(By.ID, "id_notes")
                self.slow_type(notes_input, "Test payment during automated testing")
            except:
                pass
            
            # Take screenshot before submission
            self.take_screenshot("payment-form-filled")
            
            # Submit the form
            submit_button = self.browser.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            # Wait for redirect
            self.pause_for_review(3)
            
            # Take screenshot after submission
            self.take_screenshot("after-payment-creation")
            
            # Payment might redirect to third-party page or confirmation page
            # Check for success message or payment confirmation
            confirmation_elements = self.browser.find_elements(
                By.XPATH, "//*[contains(text(), 'Payment') and (contains(text(), 'successful') or contains(text(), 'processed') or contains(text(), 'confirmed'))]"
            )
            
            if len(confirmation_elements) == 0:
                # We might be on a payment provider page, or success message is different
                # Just verify we're not on an error page
                error_messages = self.browser.find_elements(By.CSS_SELECTOR, ".alert-danger, .errorlist, .error-message")
                self.assertEqual(len(error_messages), 0, "Error message found after payment creation")
            
            # Return to rental detail page to verify payment was recorded
            self.browser.get(f"{self.live_server_url}/rentals/")
            self.pause_for_review()
            
            # Click on the same rental again
            rental_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/rentals/') and not(contains(@href, '/rentals/list'))]")
            if len(rental_links) > 0:
                rental_links[0].click()
                self.pause_for_review()
                self.take_screenshot("rental-detail-after-payment")
                
                # Look for payment history section to verify payment was recorded
                payment_sections = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'Payment History')]")
                if len(payment_sections) > 0:
                    # Verify payment amount appears in the detail
                    payment_amount_elements = self.browser.find_elements(By.XPATH, "//*[contains(text(), '50.00')]")
                    self.assertGreater(len(payment_amount_elements), 0, "Payment amount not found in rental details after payment")
            
        except Exception as e:
            self.take_screenshot("payment-creation-error")
            self.fail(f"Payment creation test failed: {str(e)}")

    def test_payment_history(self):
        """Test viewing payment history"""
        # Login as staff to see all payments
        self.login(username="staff", password="staffpass")
        
        # Try to navigate to payment history page
        try:
            # Look for payments link in navbar
            self.browser.get(f"{self.live_server_url}/")
            self.pause_for_review()
            
            # Try to find payments link
            payment_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/payments/') or contains(text(), 'Payment')]")
            if len(payment_links) > 0:
                payment_links[0].click()
            else:
                # Navigate directly to payments URL
                self.browser.get(f"{self.live_server_url}/payments/")
        except:
            # Navigate directly to payments URL
            self.browser.get(f"{self.live_server_url}/payments/")
        
        self.pause_for_review()
        self.take_screenshot("payment-history-staff")
        
        # Check for payment list elements
        payment_table = self.browser.find_elements(By.XPATH, "//table[contains(.//th/text(), 'Payment') or contains(.//th/text(), 'Amount')]")
        self.assertGreater(len(payment_table), 0, "Payment history table not found")
        
        # Test payment detail if any payments exist
        payment_detail_links = self.browser.find_elements(By.XPATH, "//a[contains(@href, '/payments/') and not(contains(@href, '/payments/list'))]")
        if len(payment_detail_links) > 0:
            payment_detail_links[0].click()
            self.pause_for_review()
            self.take_screenshot("payment-detail-page")
            
            # Verify payment detail elements
            payment_info = self.browser.find_elements(By.XPATH, "//*[contains(text(), 'Payment Details') or contains(text(), 'Payment Information')]")
            self.assertGreater(len(payment_info), 0, "Payment information not found on detail page")
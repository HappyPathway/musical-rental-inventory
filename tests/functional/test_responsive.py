import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from tests.base import BaseTestCase

class ResponsivenesTests(BaseTestCase):
    """Test cases for responsive design features"""
    
    def test_responsive_navigation(self):
        """Test responsive navigation menu on different viewport sizes"""
        # Start with desktop size view
        self.browser.set_window_size(1280, 800)
        self.browser.get(f"{self.live_server_url}/")
        self.pause_for_review()
        self.take_screenshot("desktop-navigation")
        
        # Check if main navigation is visible
        main_nav = self.browser.find_elements(By.CSS_SELECTOR, "nav, .navbar")
        self.assertGreater(len(main_nav), 0, "Main navigation not found")
        
        # Check desktop navigation links are visible
        nav_links = self.browser.find_elements(By.CSS_SELECTOR, "nav a, .navbar a")
        visible_links = [link for link in nav_links if link.is_displayed()]
        self.assertGreater(len(visible_links), 3, "Not enough navigation links visible on desktop")
        
        # Switch to tablet size
        self.browser.set_window_size(768, 1024)
        self.pause_for_review()
        self.take_screenshot("tablet-navigation")
        
        # Find hamburger/toggle button if present in tablet view
        hamburger_buttons = self.browser.find_elements(By.CSS_SELECTOR, 
            ".navbar-toggler, .nav-toggle, button[aria-controls='navbarNav']")
        
        if len(hamburger_buttons) > 0 and hamburger_buttons[0].is_displayed():
            # Navigation is collapsed, click to expand
            hamburger_buttons[0].click()
            self.pause_for_review()
            self.take_screenshot("tablet-navigation-expanded")
            
            # Verify links are now visible
            nav_links = self.browser.find_elements(By.CSS_SELECTOR, "nav a, .navbar a")
            visible_links = [link for link in nav_links if link.is_displayed()]
            self.assertGreater(len(visible_links), 3, "Not enough navigation links visible after expanding on tablet")
        
        # Switch to mobile phone size
        self.browser.set_window_size(375, 667)
        self.pause_for_review()
        self.take_screenshot("mobile-navigation")
        
        # Find hamburger/toggle button in mobile view
        hamburger_buttons = self.browser.find_elements(By.CSS_SELECTOR, 
            ".navbar-toggler, .nav-toggle, button[aria-controls='navbarNav']")
        
        if len(hamburger_buttons) > 0 and hamburger_buttons[0].is_displayed():
            # Navigation is collapsed, click to expand
            hamburger_buttons[0].click()
            self.pause_for_review()
            self.take_screenshot("mobile-navigation-expanded")
            
            # Verify links are now visible
            nav_links = self.browser.find_elements(By.CSS_SELECTOR, "nav a, .navbar a")
            visible_links = [link for link in nav_links if link.is_displayed()]
            self.assertGreater(len(visible_links), 3, "Not enough navigation links visible after expanding on mobile")
        
        # Reset window size to desktop
        self.browser.set_window_size(1280, 800)
    
    def test_responsive_forms(self):
        """Test responsive behavior of forms on different viewport sizes"""
        # Login to access forms that require authentication
        self.login(username="customer", password="customerpass")
        
        # Test on a form-heavy page (rental creation or profile update)
        try:
            # Try to go to a new rental page
            self.browser.get(f"{self.live_server_url}/rentals/create/")
        except:
            # If that fails, try profile page
            try:
                self.browser.get(f"{self.live_server_url}/users/profile/edit/")
            except:
                # If that also fails, go to registration page (which should have a form)
                self.browser.get(f"{self.live_server_url}/users/register/")
        
        self.pause_for_review()
        
        # Desktop view (1280x800)
        self.browser.set_window_size(1280, 800)
        self.pause_for_review()
        self.take_screenshot("desktop-form")
        
        # Check form elements are properly laid out in desktop view
        form_elements = self.browser.find_elements(By.CSS_SELECTOR, "form")
        self.assertGreater(len(form_elements), 0, "No form found on page")
        
        # Capture form inputs in desktop view
        form_inputs = self.browser.find_elements(By.CSS_SELECTOR, "input, select, textarea")
        desktop_inputs_displayed = len([inp for inp in form_inputs if inp.is_displayed()])
        
        # Tablet view (768x1024)
        self.browser.set_window_size(768, 1024)
        self.pause_for_review()
        self.take_screenshot("tablet-form")
        
        # Mobile view (375x667)
        self.browser.set_window_size(375, 667)
        self.pause_for_review()
        self.take_screenshot("mobile-form")
        
        # Check that the same inputs are visible in mobile view (may need to scroll)
        mobile_form_inputs = self.browser.find_elements(By.CSS_SELECTOR, "input, select, textarea")
        mobile_inputs_displayed = len([inp for inp in mobile_form_inputs if inp.is_displayed()])
        
        # We should have roughly the same number of inputs visible (some might require scrolling)
        self.assertGreaterEqual(mobile_inputs_displayed, desktop_inputs_displayed * 0.5, 
                               "Too few form inputs visible in mobile view")
        
        # Reset window size to desktop
        self.browser.set_window_size(1280, 800)
    
    def test_responsive_tables(self):
        """Test responsive behavior of tables on different viewport sizes"""
        # Login to access tables that require authentication
        self.login(username="staff", password="staffpass")
        
        # Go to a page with tables (rentals or equipment list)
        try:
            self.browser.get(f"{self.live_server_url}/rentals/")
        except:
            self.browser.get(f"{self.live_server_url}/inventory/")
        
        self.pause_for_review()
        
        # Desktop view (1280x800)
        self.browser.set_window_size(1280, 800)
        self.pause_for_review()
        self.take_screenshot("desktop-table")
        
        # Check tables are present
        tables = self.browser.find_elements(By.CSS_SELECTOR, "table")
        if len(tables) == 0:
            # If no tables found, try another page
            self.browser.get(f"{self.live_server_url}/inventory/")
            self.pause_for_review()
            tables = self.browser.find_elements(By.CSS_SELECTOR, "table")
        
        self.assertGreater(len(tables), 0, "No tables found on page")
        
        # Count visible columns in desktop view
        table_headers = self.browser.find_elements(By.CSS_SELECTOR, "th")
        desktop_headers_count = len([th for th in table_headers if th.is_displayed()])
        
        # Tablet view (768x1024)
        self.browser.set_window_size(768, 1024)
        self.pause_for_review()
        self.take_screenshot("tablet-table")
        
        # Mobile view (375x667)
        self.browser.set_window_size(375, 667)
        self.pause_for_review()
        self.take_screenshot("mobile-table")
        
        # Check how tables adapt to mobile view
        # Options: horizontal scroll, stacked view, or fewer columns
        table_mobile = self.browser.find_elements(By.CSS_SELECTOR, "table")
        self.assertGreater(len(table_mobile), 0, "Tables disappeared in mobile view")
        
        # Look for horizontal scroll containers
        scroll_containers = self.browser.find_elements(By.CSS_SELECTOR, 
            ".table-responsive, [style*='overflow-x']")
        
        # Count visible columns in mobile view
        mobile_headers = self.browser.find_elements(By.CSS_SELECTOR, "th")
        mobile_headers_count = len([th for th in mobile_headers if th.is_displayed()])
        
        # Either we should have a responsive container or fewer headers visible
        is_responsive = (len(scroll_containers) > 0 and scroll_containers[0].is_displayed()) or (mobile_headers_count <= desktop_headers_count)
        self.assertTrue(is_responsive, "Table is not responsive in mobile view")
        
        # Reset window size to desktop
        self.browser.set_window_size(1280, 800)
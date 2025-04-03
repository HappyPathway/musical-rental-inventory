import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from inventory.models import Equipment, Category
from users.models import UserProfile
from rentals.models import Rental

User = get_user_model()

@pytest.mark.django_db
class TestBaseTemplate:
    """Test cases for base template and template inheritance"""
    
    def test_base_template_navigation(self, test_user):
        """Test that base template contains required navigation elements"""
        client = Client()
        client.force_login(test_user)
        response = client.get(reverse('inventory:equipment_list'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test navigation elements
        nav = soup.find('nav', class_='navbar')
        assert nav is not None, "Navigation element not found"
        
        # Test main navigation links
        nav_links = [a.get('href') for a in nav.find_all('a')]
        expected_links = [
            reverse('inventory:equipment_list'),
            reverse('rentals:rental_list'),
        ]
        for link in expected_links:
            assert link in nav_links, f"Expected link {link} not found in navigation"
        
        # Test user menu
        user_dropdown = soup.find('a', class_='nav-link', string=lambda text: text and test_user.username in text)
        assert user_dropdown is not None, "Username not found in navigation"
    
    def test_staff_specific_navigation(self, test_staff):
        """Test staff-specific navigation elements"""
        client = Client()
        client.force_login(test_staff)
        response = client.get(reverse('inventory:equipment_list'))
        
        assert response.status_code == 200, "Response should be successful"
        assert response.context['user'].is_staff, "User should be staff"
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test staff menu
        nav = soup.find('nav', class_='navbar')
        assert nav is not None, "Navigation bar not found"
        
        navbar_nav = nav.find('div', class_='collapse navbar-collapse')
        assert navbar_nav is not None, "Navbar collapse not found"
        
        staff_dropdown = navbar_nav.find('li', class_='nav-item dropdown')
        assert staff_dropdown is not None, "Staff dropdown not found"
        
        staff_menu = staff_dropdown.find('a', class_='nav-link dropdown-toggle')
        assert staff_menu is not None, "Staff menu not found"
        assert 'Inventory Tools' in staff_menu.text, "Staff menu text not found"
        
        # Test staff dropdown items
        dropdown_menu = staff_dropdown.find('ul', class_='dropdown-menu')
        assert dropdown_menu is not None, "Staff dropdown menu not found"
        
        # Test inventory tool links
        inventory_links = [
            reverse('inventory:equipment_add'),
            reverse('inventory:equipment_scan'),
        ]
        nav_links = [a.get('href') for a in soup.find_all('a')]
        for link in inventory_links:
            assert link in nav_links, f"Inventory tool link {link} not found"
            
        # Test admin link in user menu section
        admin_link = soup.find('a', class_='nav-link', href=reverse('admin:index'))
        assert admin_link is not None, "Admin link not found in user menu"

@pytest.mark.django_db
class TestInventoryTemplates:
    """Test cases for inventory-related templates"""
    
    def test_equipment_list_template(self, test_equipment, test_user):
        """Test equipment list template content and structure"""
        client = Client()
        client.force_login(test_user)
        response = client.get(reverse('inventory:equipment_list'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test page title
        assert "Equipment Inventory" in str(soup), "Page title not found"
        
        # Test filter form
        filter_form = soup.find('form', class_='filter-form')
        assert filter_form is not None, "Filter form not found"
        assert filter_form.find('input', {'name': 'search'}) is not None, "Search input not found"
        assert filter_form.find('select', {'name': 'category'}) is not None, "Category select not found"
        assert filter_form.find('select', {'name': 'status'}) is not None, "Status select not found"
        
        # Test equipment grid
        equipment_grid = soup.find('div', class_='row-cols-1')
        assert equipment_grid is not None, "Equipment grid not found"
        
        # Test equipment cards
        equipment_cards = soup.find_all('div', class_='equipment-card')
        assert len(equipment_cards) > 0, "No equipment cards found"
        
        # Test card content
        first_card = equipment_cards[0]
        assert first_card.find('h5', class_='card-title') is not None, "Card title not found"
        assert first_card.find('span', class_='price-tag') is not None, "Price tag not found"
        
        # Test equipment status badge
        status_badge = first_card.find('span', class_=lambda x: x and 'badge' in x)
        if test_equipment.status != 'available':
            assert status_badge is not None, "Status badge not found for non-available equipment"
            assert test_equipment.get_status_display() in status_badge.text, "Status text not found in badge"

    def test_equipment_detail_template(self, test_equipment, test_user):
        """Test equipment detail template content and structure"""
        client = Client()
        client.force_login(test_user)
        response = client.get(
            reverse('inventory:equipment_detail', kwargs={'pk': test_equipment.pk})
        )
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test equipment details
        details = soup.find('div', class_='card')
        assert details is not None, "Equipment details card not found"
        
        # Test required information
        assert test_equipment.name in str(soup), "Equipment name not found"
        assert test_equipment.brand in str(soup), "Equipment brand not found"
        assert str(test_equipment.category) in str(soup), "Equipment category not found"
        
        # Test pricing information
        assert str(test_equipment.rental_price_daily) in str(soup), "Daily price not found"
        assert str(test_equipment.rental_price_weekly) in str(soup), "Weekly price not found"
        assert str(test_equipment.rental_price_monthly) in str(soup), "Monthly price not found"
        
        # Test action buttons for staff
        if test_user.is_staff:
            edit_link = soup.find('a', href=reverse('inventory:equipment_edit', 
                                                  kwargs={'pk': test_equipment.pk}))
            assert edit_link is not None, "Edit link not found for staff user"

@pytest.mark.django_db
class TestUserTemplates:
    """Test cases for user-related templates"""
    
    def test_login_template(self):
        """Test login template content and structure"""
        client = Client()
        response = client.get(reverse('users:login'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test login form
        form = soup.find('form')
        assert form is not None, "Login form not found"
        assert form.find('input', {'name': 'username'}) is not None, "Username input not found"
        assert form.find('input', {'name': 'password'}) is not None, "Password input not found"
        assert form.find('button', {'type': 'submit'}) is not None, "Submit button not found"
        
        # Test registration link
        register_link = soup.find('a', href=reverse('users:register'))
        assert register_link is not None, "Registration link not found"

    def test_profile_template(self, test_user):
        """Test user profile template content and structure"""
        client = Client()
        client.force_login(test_user)
        response = client.get(reverse('users:view_profile'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test profile information
        profile_card = soup.find('div', class_='card')
        assert profile_card is not None, "Profile card not found"
        
        # Test user information display
        assert test_user.username in str(soup), "Username not found"
        assert test_user.email in str(soup), "Email not found"
        
        # Test edit profile link
        edit_link = soup.find('a', href=reverse('users:update_profile'))
        assert edit_link is not None, "Edit profile link not found"

@pytest.mark.django_db
class TestRentalTemplates:
    """Test cases for rental-related templates"""
    
    def test_rental_list_template(self, test_rental, test_user):
        """Test rental list template content and structure"""
        client = Client()
        client.force_login(test_user)
        response = client.get(reverse('rentals:rental_list'))
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test rental table
        rental_table = soup.find('table', class_='table')
        assert rental_table is not None, "Rental table not found"
        
        # Test rental information display
        customer_name = f"{test_rental.customer.first_name} {test_rental.customer.last_name}"
        assert customer_name in str(soup), "Customer name not found"
        assert test_rental.status in str(soup), "Rental status not found"
        
        # Test status filters
        status_filters = soup.find_all('a', class_=lambda x: x and 'btn-sm' in x)
        expected_statuses = ['active', 'pending', 'overdue', 'completed', 'cancelled']
        status_links = [a.get('href') for a in status_filters]
        for status in expected_statuses:
            assert f"?status={status}" in str(status_links), f"Status filter for {status} not found"
        
        # Test search form
        search_form = soup.find('form', class_='d-flex')
        assert search_form is not None, "Search form not found"
        assert search_form.find('input', {'name': 'q'}) is not None, "Search input not found"

    def test_rental_detail_template(self, test_rental, test_user):
        """Test rental detail template content and structure"""
        client = Client()
        client.force_login(test_user)
        response = client.get(
            reverse('rentals:rental_detail', kwargs={'pk': test_rental.pk})
        )
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test rental details
        details = soup.find('div', class_='card')
        assert details is not None, "Rental details card not found"
        
        # Test required information
        customer_name = f"{test_rental.customer.first_name} {test_rental.customer.last_name}"
        assert customer_name in str(soup), "Customer name not found"
        assert test_rental.status in str(soup), "Rental status not found"
        
        # Test rental items section
        items_table = soup.find('table', class_='table')
        assert items_table is not None, "Rental items table not found"
        
        # Test status-specific actions
        if test_rental.status == 'pending':
            cancel_link = soup.find('a', href=reverse('rentals:rental_cancel', kwargs={'pk': test_rental.pk}))
            assert cancel_link is not None, "Cancel link not found for pending rental"
        elif test_rental.status == 'active':
            return_link = soup.find('a', href=reverse('rentals:rental_return', kwargs={'pk': test_rental.pk}))
            assert return_link is not None, "Return link not found for active rental"
        
        # Test financial information
        assert str(test_rental.total_price) in str(soup), "Total price not found"
        assert str(test_rental.deposit_total) in str(soup), "Deposit amount not found" 
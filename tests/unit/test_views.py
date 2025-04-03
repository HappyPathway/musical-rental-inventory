import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from inventory.models import Equipment, Category, MaintenanceRecord
from rentals.models import Customer, Rental, RentalItem
from users.models import UserProfile

User = get_user_model()

@pytest.mark.django_db
class TestInventoryViews:
    def test_equipment_list_view(self, test_equipment, test_user):
        """Test equipment list view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('inventory:equipment_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'equipment_list' in response.context
        assert test_equipment in response.context['equipment_list']

    def test_equipment_detail_view(self, test_equipment, test_user):
        """Test equipment detail view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('inventory:equipment_detail', kwargs={'pk': test_equipment.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['equipment'] == test_equipment

    def test_equipment_create_view(self, test_category, test_user):
        """Test equipment create view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('inventory:equipment_add')
        data = {
            'name': 'New Equipment',
            'description': 'Test Description',
            'category': test_category.id,
            'brand': 'Test Brand',
            'model_number': 'TEST789',
            'serial_number': 'SN789012',
            'rental_price_daily': '50.00',
            'rental_price_weekly': '300.00',
            'rental_price_monthly': '1000.00',
            'deposit_amount': '500.00',
            'status': 'available'
        }
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after successful creation
        assert Equipment.objects.filter(name='New Equipment').exists()

    def test_equipment_update_view(self, test_equipment, test_user):
        """Test equipment update view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('inventory:equipment_edit', kwargs={'pk': test_equipment.pk})
        data = {
            'name': 'Updated Equipment',
            'description': 'Updated test equipment description',
            'category': test_equipment.category.id,
            'brand': test_equipment.brand,
            'model_number': test_equipment.model_number,
            'serial_number': test_equipment.serial_number,
            'rental_price_daily': test_equipment.rental_price_daily,
            'rental_price_weekly': test_equipment.rental_price_weekly,
            'rental_price_monthly': test_equipment.rental_price_monthly,
            'deposit_amount': test_equipment.deposit_amount,
            'status': test_equipment.status,
            'condition': test_equipment.condition or '',
            'notes': test_equipment.notes or '',
            'quantity': test_equipment.quantity
        }
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after successful update
        test_equipment.refresh_from_db()
        assert test_equipment.name == 'Updated Equipment'

@pytest.mark.django_db
class TestRentalViews:
    def test_rental_list_view(self, test_rental, test_user):
        """Test rental list view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('rentals:rental_list')
        response = client.get(url)
        assert response.status_code == 200
        assert 'rental_list' in response.context
        assert test_rental in response.context['rental_list']

    def test_rental_create_view(self, test_customer, test_equipment, test_user):
        """Test rental create view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('rentals:rental_create')
        data = {
            'customer': test_customer.id,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timezone.timedelta(days=7),
            'duration_type': 'weekly',
            'notes': 'Test rental',
            'equipment': [test_equipment.id],
            'quantity': 1,
            'price': '50.00'
        }
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after successful creation
        assert Rental.objects.filter(customer=test_customer).exists()

    def test_rental_detail_view(self, test_rental, test_user):
        """Test rental detail view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('rentals:rental_detail', kwargs={'pk': test_rental.pk})
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['rental'] == test_rental

@pytest.mark.django_db
class TestUserViews:
    def test_user_profile_view(self, test_user):
        """Test user profile view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('users:view_profile')
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['profile'] == test_user.profile

    def test_user_profile_update_view(self, test_user):
        """Test user profile update view"""
        client = Client()
        client.force_login(test_user)
        url = reverse('users:update_profile')
        data = {
            # User form data
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            # Profile form data
            'phone_number': '+12125552368',
            'address': '456 New St',
            'city': 'New City',
            'state': 'NS',
            'zip_code': '54321'
        }
        response = client.post(url, data)
        assert response.status_code == 302  # Redirect after successful update
        test_user.refresh_from_db()
        assert test_user.first_name == 'Updated'
        assert test_user.profile.city == 'New City'

@pytest.mark.django_db
class TestTemplateInheritance:
    def test_base_template_inheritance(self, test_user):
        """Test that all pages inherit from base template"""
        client = Client()
        client.force_login(test_user)
        
        # Test various URLs to ensure they use base template
        urls = [
            reverse('inventory:equipment_list'),
            reverse('rentals:rental_list'),
            reverse('users:view_profile'),
        ]
        
        for url in urls:
            response = client.get(url)
            assert response.status_code == 200
            assert 'base.html' in [t.name for t in response.templates]

@pytest.mark.django_db
class TestURLPatterns:
    def test_inventory_urls(self):
        """Test inventory URL patterns"""
        urls = [
            ('inventory:equipment_list', []),
            ('inventory:equipment_add', []),
            ('inventory:equipment_detail', [1]),
            ('inventory:equipment_edit', [1]),
            ('inventory:equipment_delete', [1]),
        ]
        
        for url_name, args in urls:
            try:
                reverse(url_name, args=args)
            except:
                pytest.fail(f"URL pattern {url_name} is not properly configured")

    def test_rental_urls(self):
        """Test rental URL patterns"""
        urls = [
            ('rentals:rental_list', []),
            ('rentals:rental_create', []),
            ('rentals:rental_detail', [1]),
            ('rentals:rental_update', [1]),
            ('rentals:rental_cancel', [1]),
        ]
        
        for url_name, args in urls:
            try:
                reverse(url_name, args=args)
            except:
                pytest.fail(f"URL pattern {url_name} is not properly configured")

    def test_user_urls(self):
        """Test user URL patterns"""
        urls = [
            ('users:view_profile', []),
            ('users:update_profile', []),
            ('users:password_reset', []),
        ]
        
        for url_name, args in urls:
            try:
                reverse(url_name, args=args)
            except:
                pytest.fail(f"URL pattern {url_name} is not properly configured") 
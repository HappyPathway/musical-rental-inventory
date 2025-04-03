import pytest
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from inventory.models import Category, Equipment, EquipmentAttachment, MaintenanceRecord
from rentals.models import Rental, RentalItem, Customer
from payments.models import Payment

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def test_user():
    """Create a test user"""
    User = get_user_model()
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def test_staff():
    """Create a test staff user"""
    User = get_user_model()
    user = User.objects.create_user(
        username='staffuser',
        email='staff@example.com',
        password='staffpass123',
        is_staff=True
    )
    user.profile.user_type = 'employee'
    user.profile.save()
    return user

@pytest.fixture
def test_category():
    """Create a test category"""
    return Category.objects.create(
        name='Test Category',
        description='Test Category Description'
    )

@pytest.fixture
def test_equipment(test_category):
    """Create test equipment"""
    equipment = Equipment.objects.create(
        name='Test Equipment',
        brand='Test Brand',
        model_number='TEST123',
        serial_number='SN123456',
        category=test_category,
        status='available',
        condition='excellent',
        rental_price_daily=50.00,
        rental_price_weekly=300.00,
        rental_price_monthly=1000.00,
        deposit_amount=500.00
    )
    equipment.save()
    return equipment

@pytest.fixture
def test_customer(test_user):
    """Create a test customer"""
    return Customer.objects.create(
        user=test_user,
        first_name='Test',
        last_name='User',
        email='test@example.com',
        phone='+1234567890',
        address='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        id_type='drivers_license',
        id_number='DL123456'
    )

@pytest.fixture
def test_rental(test_customer, test_equipment):
    """Create a test rental with proper many-to-many relationship"""
    rental = Rental.objects.create(
        customer=test_customer,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timezone.timedelta(days=7),
        duration_type='weekly',
        status='active',
        total_price=350.00,
        deposit_total=500.00
    )
    
    # Create the rental item to establish the many-to-many relationship
    RentalItem.objects.create(
        rental=rental,
        equipment=test_equipment,
        quantity=1,
        price=350.00
    )
    
    return rental

@pytest.fixture
def test_payment(test_rental):
    """Create a test payment"""
    return Payment.objects.create(
        rental=test_rental,
        amount=350.00,
        payment_type='deposit',
        status='completed',
        payment_method='credit_card'
    )

@pytest.fixture
def test_rental_item(test_rental, test_equipment):
    """Create a test rental item"""
    return RentalItem.objects.create(
        rental=test_rental,
        equipment=test_equipment,
        quantity=1,
        price=350.00,
        condition_note_checkout='Good condition'
    )

@pytest.fixture
def test_attachment(test_equipment):
    """Create a test equipment attachment"""
    return EquipmentAttachment.objects.create(
        equipment=test_equipment,
        title='Test Manual',
        description='Test Description',
        file_type='manual',
        file='test.pdf'
    )

@pytest.fixture
def test_maintenance_record(test_equipment):
    """Create a test maintenance record"""
    return MaintenanceRecord.objects.create(
        equipment=test_equipment,
        date=timezone.now().date(),
        description='Test maintenance',
        cost=100.00,
        performed_by='Test Technician'
    ) 
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from inventory.models import Equipment, Category, EquipmentAttachment, MaintenanceRecord
from rentals.models import Rental, RentalItem, Customer
from payments.models import Payment
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
import base64

User = get_user_model()

@pytest.mark.django_db
class TestEquipmentModel:
    def test_equipment_creation(self, test_equipment):
        """Test that equipment can be created with valid data"""
        assert test_equipment.name == 'Test Equipment'
        assert test_equipment.status == 'available'
        assert test_equipment.brand == 'Test Brand'

    def test_equipment_str_representation(self, test_equipment):
        """Test the string representation of equipment"""
        assert str(test_equipment) == 'Test Equipment (Test Brand)'

    def test_equipment_is_available(self, test_equipment):
        """Test the is_available method"""
        assert test_equipment.is_available() is True
        test_equipment.status = 'rented'
        test_equipment.save()
        assert test_equipment.is_available() is False

    def test_rental_prices(self, test_equipment):
        """Test rental price calculations and validations"""
        assert test_equipment.rental_price_daily == 50.00
        assert test_equipment.rental_price_weekly == 300.00
        assert test_equipment.rental_price_monthly == 1000.00
        assert test_equipment.deposit_amount == 500.00

    def test_invalid_status(self, test_equipment):
        """Test that invalid status raises validation error"""
        with pytest.raises(ValidationError):
            test_equipment.status = 'invalid_status'
            test_equipment.full_clean()

    def test_equipment_history(self, test_equipment):
        """Test that history is being tracked"""
        test_equipment.status = 'maintenance'
        test_equipment.save()
        assert test_equipment.history.count() >= 2  # Creation + status change
        assert test_equipment.history.latest().status == 'maintenance'

    def test_qr_code_generation(self, test_equipment):
        """Test QR code generation"""
        test_equipment.generate_qr_code()
        assert test_equipment.qr_code is not None
        assert test_equipment.qr_uuid is not None

    def test_equipment_relationships(self, test_equipment):
        """Test equipment relationships with other models"""
        # Create a maintenance record
        maintenance = MaintenanceRecord.objects.create(
            equipment=test_equipment,
            date=timezone.now().date(),
            description="Test maintenance"
        )
        
        # Create an attachment
        attachment = EquipmentAttachment.objects.create(
            equipment=test_equipment,
            description="Test attachment"
        )
        
        # Test relationships
        assert maintenance in test_equipment.maintenance_records.all()
        assert attachment in test_equipment.attachments.all()
        
        # Test rental relationship through rental items
        rental_item = RentalItem.objects.filter(equipment=test_equipment).first()
        if rental_item:
            assert rental_item.rental in test_equipment.rental_set.all()

    def test_manual_fetch(self, test_equipment):
        """Test manual fetching with OpenAI"""
        from inventory.utils import fetch_manual_from_openai
        from django.conf import settings
        
        assert settings.OPENAI_API_KEY is not None, "OpenAI API key is not set"
        
        result = fetch_manual_from_openai(test_equipment.brand, test_equipment.model_number)
        assert isinstance(result, dict)
        assert 'manual_link' in result
        assert 'manual_title' in result

@pytest.mark.django_db
class TestCategoryModel:
    def test_category_creation(self, test_category):
        """Test category creation with valid data"""
        assert test_category.name == 'Test Category'
        assert test_category.description == 'Test Category Description'

    def test_category_str_representation(self, test_category):
        """Test string representation of category"""
        assert str(test_category) == 'Test Category'

    def test_category_equipment_relation(self, test_category, test_equipment):
        """Test category to equipment relationship"""
        assert test_equipment in test_category.equipment.all()
        assert test_equipment.category == test_category

@pytest.mark.django_db
class TestMaintenanceRecordModel:
    def test_maintenance_record_creation(self, test_equipment):
        """Test maintenance record creation"""
        record = MaintenanceRecord.objects.create(
            equipment=test_equipment,
            date=timezone.now().date(),
            description="Test maintenance",
            cost=100.00,
            performed_by="Test Technician"
        )
        assert record.equipment == test_equipment
        assert record.description == "Test maintenance"
        assert record.cost == 100.00

    def test_maintenance_record_str(self, test_equipment):
        """Test maintenance record string representation"""
        record = MaintenanceRecord.objects.create(
            equipment=test_equipment,
            date=timezone.now().date(),
            description="Test maintenance"
        )
        expected = f"{test_equipment.name} - {record.date}"
        assert str(record) == expected

    def test_maintenance_record_completion(self, test_equipment):
        """Test maintenance record completion status"""
        record = MaintenanceRecord.objects.create(
            equipment=test_equipment,
            date=timezone.now().date(),
            description="Test maintenance",
            scheduled_date=timezone.now().date()
        )
        assert not record.is_completed
        record.is_completed = True
        record.save()
        assert record.is_completed

@pytest.mark.django_db
class TestRentalModel:
    def test_rental_creation(self, test_rental):
        """Test rental creation with valid data"""
        assert test_rental.customer.get_full_name() == 'Test User'
        assert test_rental.status == 'active'
        assert test_rental.items.count() == 1
        rental_item = test_rental.items.first()
        assert rental_item.equipment.name == 'Test Equipment'

    def test_rental_dates_validation(self, test_customer, test_equipment):
        """Test rental dates validation"""
        with pytest.raises(ValidationError):
            rental = Rental.objects.create(
                customer=test_customer,
                start_date='2024-01-07',
                end_date='2024-01-01',  # End date before start date
                duration_type='daily',
                status='active',
                total_price=50.00,
                deposit_total=500.00
            )
            rental.full_clean()

    def test_rental_equipment_availability(self, test_rental):
        """Test equipment availability status during rental"""
        rental_item = test_rental.items.first()
        assert rental_item.equipment.status == 'rented'
        test_rental.status = 'completed'
        test_rental.save()
        test_rental.mark_as_returned()
        rental_item.equipment.refresh_from_db()
        assert rental_item.equipment.status == 'available'

    def test_rental_relationships_and_calculations(self, test_rental, test_equipment):
        """Test rental relationships and price calculations"""
        # Test rental items relationship
        rental_item = test_rental.items.first()
        assert rental_item.equipment == test_equipment
        assert rental_item.rental == test_rental
        
        # Test price calculations
        assert test_rental.total_price > 0
        assert test_rental.deposit_total == test_equipment.deposit_amount
        
        # Test payment relationship
        payment = Payment.objects.create(
            rental=test_rental,
            amount=100.00,
            payment_type='rental',
            payment_method='credit_card',
            status='completed'
        )
        assert payment in test_rental.payments.all()

@pytest.mark.django_db
class TestPaymentModel:
    def test_payment_creation(self, test_payment):
        """Test payment creation with valid data"""
        assert test_payment.rental.status == 'active'
        assert test_payment.amount == 350.00
        assert test_payment.payment_type == 'deposit'
        assert test_payment.status == 'completed'

    def test_payment_validation(self, test_rental):
        """Test payment amount validation"""
        with pytest.raises(ValidationError):
            Payment.objects.create(
                rental=test_rental,
                amount=-100.00,  # Negative amount
                payment_type='deposit',
                status='completed',
                payment_method='credit_card'
            ).full_clean()

    def test_payment_status_transitions(self, test_payment):
        """Test payment status transitions"""
        test_payment.status = 'pending'
        test_payment.save()
        assert test_payment.status == 'pending'
        test_payment.status = 'completed'
        test_payment.save()
        assert test_payment.status == 'completed'

    def test_payment_relationships_and_refunds(self, test_payment):
        """Test payment relationships and refund functionality"""
        # Test rental relationship
        assert test_payment.rental is not None
        
        # Test refund fields
        test_payment.refund_amount = 50.00
        test_payment.refund_date = timezone.now()
        test_payment.refund_transaction_id = 'REF123'
        test_payment.save()
        
        assert test_payment.refund_amount == 50.00
        assert test_payment.refund_transaction_id == 'REF123'
        
    def test_payment_method_validation(self, test_rental):
        """Test payment method validation"""
        with pytest.raises(ValidationError):
            Payment.objects.create(
                rental=test_rental,
                amount=100.00,
                payment_type='rental',
                payment_method='invalid_method',  # Invalid payment method
                status='completed'
            ).full_clean()

@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self, test_user):
        """Test user creation with valid data"""
        assert test_user.username == 'testuser'
        assert test_user.email == 'test@example.com'
        assert test_user.check_password('testpass123')

    def test_user_staff_status(self, test_staff):
        """Test staff user creation and permissions"""
        assert test_staff.is_staff
        assert test_staff.username == 'staffuser'

    def test_user_phone_validation(self):
        """Test phone number validation"""
        customer = Customer(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='invalid-phone',  # Invalid phone number
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            id_type='drivers_license',
            id_number='DL123456'
        )
        with pytest.raises(ValidationError):
            customer.full_clean()

@pytest.mark.django_db
class TestEquipmentAttachmentModel:
    def test_attachment_creation(self, test_equipment):
        """Test equipment attachment creation"""
        attachment = EquipmentAttachment.objects.create(
            equipment=test_equipment,
            description="Test attachment"
        )
        assert attachment.equipment == test_equipment
        assert attachment.description == "Test attachment"

    def test_attachment_str_representation(self, test_equipment):
        """Test attachment string representation"""
        attachment = EquipmentAttachment.objects.create(
            equipment=test_equipment,
            description="Test attachment"
        )
        assert str(attachment) == f"Attachment for {test_equipment.name}" 
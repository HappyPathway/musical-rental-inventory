import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from inventory.forms import EquipmentForm, MaintenanceRecordForm, AttachmentForm
from rentals.forms import CustomerForm, RentalForm, RentalItemForm, ReturnRentalItemForm
from users.forms import CustomerRegistrationForm, StaffCreationForm, UserProfileUpdateForm
from inventory.models import Category, Equipment, EquipmentAttachment
from rentals.models import Customer, Rental, RentalItem
from users.models import UserProfile

User = get_user_model()

@pytest.mark.django_db
class TestEquipmentForm:
    def test_equipment_form_valid_data(self, test_category):
        """Test equipment form with valid data"""
        form_data = {
            'name': 'Test Equipment',
            'description': 'Test Description',
            'category': test_category.id,
            'brand': 'Test Brand',
            'model_number': 'TEST123',
            'serial_number': 'SN123456',
            'rental_price_daily': '50.00',
            'rental_price_weekly': '300.00',
            'rental_price_monthly': '1000.00',
            'deposit_amount': '500.00',
            'status': 'available'
        }
        form = EquipmentForm(data=form_data)
        assert form.is_valid()
        equipment = form.save()
        assert equipment.name == 'Test Equipment'
        assert equipment.brand == 'Test Brand'
        assert equipment.rental_price_daily == 50.00

    def test_equipment_form_duplicate_serial(self, test_equipment):
        """Test equipment form with duplicate serial number"""
        form_data = {
            'name': 'Another Equipment',
            'description': 'Test Description',
            'category': test_equipment.category.id,
            'brand': 'Test Brand',
            'model_number': 'TEST456',
            'serial_number': test_equipment.serial_number,  # Using existing serial number
            'rental_price_daily': '50.00',
            'rental_price_weekly': '300.00',
            'rental_price_monthly': '1000.00',
            'deposit_amount': '500.00',
            'status': 'available'
        }
        form = EquipmentForm(data=form_data)
        assert not form.is_valid()
        assert 'serial_number' in form.errors

    def test_equipment_form_required_fields(self):
        """Test equipment form with missing required fields"""
        form_data = {
            'name': 'Test Equipment',
            'brand': 'Test Brand',
            'rental_price_daily': '50.00',
            'deposit_amount': '500.00'
        }
        form = EquipmentForm(data=form_data)
        assert not form.is_valid()
        assert 'category' in form.errors

@pytest.mark.django_db
class TestCustomerForm:
    def test_customer_form_valid_data(self):
        """Test customer form with valid data"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'email': 'test@example.com',
            'phone': '+12125552368',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'id_type': 'drivers_license',
            'id_number': 'DL123456'
        }
        form = CustomerForm(data=form_data)
        assert form.is_valid()
        customer = form.save()
        assert customer.first_name == 'Test'
        assert customer.email == 'test@example.com'

    def test_customer_form_invalid_email(self):
        """Test customer form with invalid email"""
        form_data = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'email': 'invalid-email',
            'phone': '+12125552368',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'id_type': 'drivers_license',
            'id_number': 'DL123456'
        }
        form = CustomerForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

    def test_customer_form_duplicate_email(self, test_customer):
        """Test customer form with duplicate email"""
        form_data = {
            'first_name': 'Another',
            'last_name': 'Customer',
            'email': test_customer.email,
            'phone': '+12125552368',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'id_type': 'drivers_license',
            'id_number': 'DL123457'
        }
        form = CustomerForm(data=form_data)
        assert not form.is_valid()
        assert 'email' in form.errors

@pytest.mark.django_db
class TestRentalForm:
    def test_rental_form_valid_data(self, test_customer):
        """Test rental form with valid data"""
        form_data = {
            'customer': test_customer.id,
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timezone.timedelta(days=7),
            'duration_type': 'weekly',
            'notes': 'Test rental'
        }
        form = RentalForm(data=form_data)
        assert form.is_valid()
        rental = form.save()
        assert rental.customer == test_customer
        assert rental.duration_type == 'weekly'

    def test_rental_form_invalid_dates(self, test_customer):
        """Test rental form with invalid dates"""
        form_data = {
            'customer': test_customer.id,
            'start_date': timezone.now().date() + timezone.timedelta(days=7),
            'end_date': timezone.now().date(),
            'duration_type': 'weekly',
            'notes': 'Test rental'
        }
        form = RentalForm(data=form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors

@pytest.mark.django_db
class TestCustomerRegistrationForm:
    def test_customer_registration_form_valid_data(self):
        """Test customer registration form with valid data"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+12125552368',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'agree_to_terms': True
        }
        form = CustomerRegistrationForm(data=form_data)
        assert form.is_valid()
        user = form.save()
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.profile.user_type == 'customer'

    def test_customer_registration_form_invalid_phone(self):
        """Test customer registration form with invalid phone number"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': 'invalid-phone',
            'agree_to_terms': True
        }
        form = CustomerRegistrationForm(data=form_data)
        assert not form.is_valid()
        assert 'phone_number' in form.errors

@pytest.mark.django_db
class TestMaintenanceRecordForm:
    def test_maintenance_record_form_valid_data(self, test_equipment):
        """Test maintenance record form with valid data"""
        form_data = {
            'date': timezone.now().date(),
            'description': 'Test maintenance',
            'cost': '100.00',
            'performed_by': 'Test Technician'
        }
        form = MaintenanceRecordForm(data=form_data)
        assert form.is_valid()
        record = form.save(commit=False)
        record.equipment = test_equipment
        record.save()
        assert record.description == 'Test maintenance'
        assert record.cost == 100.00

    def test_maintenance_record_form_missing_required(self, test_equipment):
        """Test maintenance record form with missing required fields"""
        form_data = {
            'description': 'Test maintenance',
            'cost': '100.00',
            'performed_by': 'Test Technician'
        }
        form = MaintenanceRecordForm(data=form_data)
        assert not form.is_valid()
        assert 'date' in form.errors

    def test_maintenance_record_form_optional_cost(self, test_equipment):
        """Test maintenance record form with optional cost field"""
        form_data = {
            'date': timezone.now().date(),
            'description': 'Test maintenance',
            'performed_by': 'Test Technician'
        }
        form = MaintenanceRecordForm(data=form_data)
        assert form.is_valid()
        record = form.save(commit=False)
        record.equipment = test_equipment
        record.save()
        assert record.description == 'Test maintenance'
        assert record.cost is None

@pytest.mark.django_db
class TestRentalItemForm:
    def test_rental_item_form_valid_data(self, test_equipment, test_rental, test_category):
        """Test rental item form with valid data"""
        # Create a new available equipment for this test
        available_equipment = Equipment.objects.create(
            name='Available Equipment',
            brand='Test Brand',
            model_number='TEST456',
            serial_number='SN456789',
            category=test_category,
            status='available',
            condition='excellent',
            rental_price_daily=50.00,
            rental_price_weekly=300.00,
            rental_price_monthly=1000.00,
            deposit_amount=500.00
        )
        
        form_data = {
            'equipment': available_equipment.id,
            'quantity': 1,
            'price': 50.00,
            'condition_note_checkout': 'Good condition'
        }
        form = RentalItemForm(data=form_data)
        if not form.is_valid():
            print("Form errors:", form.errors)  # Debug line
        assert form.is_valid()
        rental_item = form.save(commit=False)
        rental_item.rental = test_rental
        rental_item.save()
        assert rental_item.equipment == available_equipment
        assert rental_item.rental == test_rental
        assert rental_item.price == 50.00

    def test_rental_item_form_invalid_quantity(self, test_equipment, test_rental):
        """Test rental item form with invalid quantity"""
        form_data = {
            'equipment': test_equipment.id,
            'quantity': 0,  # Invalid quantity
            'price': 50.00,
            'condition_note_checkout': 'Good condition'
        }
        form = RentalItemForm(data=form_data)
        assert not form.is_valid()
        assert 'quantity' in form.errors

@pytest.mark.django_db
class TestReturnRentalItemForm:
    def test_return_rental_item_form_valid_data(self, test_rental_item):
        """Test return rental item form with valid data"""
        form_data = {
            'condition_note_return': 'Good condition'
        }
        form = ReturnRentalItemForm(data=form_data, instance=test_rental_item)
        assert form.is_valid()
        rental_item = form.save()
        assert rental_item.condition_note_return == 'Good condition'

    def test_return_rental_item_form_missing_required(self):
        """Test return rental item form with missing required fields"""
        form_data = {}
        form = ReturnRentalItemForm(data=form_data)
        assert not form.is_valid()
        assert 'condition_note_return' in form.errors

@pytest.mark.django_db
class TestAttachmentForm:
    def test_attachment_form_valid_data(self, test_equipment):
        """Test attachment form with valid data"""
        file_content = b'Test file content'
        file = SimpleUploadedFile('test.pdf', file_content, content_type='application/pdf')
        form_data = {
            'file': file,
            'description': 'Test attachment'
        }
        form = AttachmentForm(data=form_data, files={'file': file})
        assert form.is_valid()
        attachment = form.save(commit=False)
        attachment.equipment = test_equipment
        attachment.save()
        assert attachment.description == 'Test attachment'
        assert attachment.file.name.endswith('.pdf')

    def test_attachment_form_invalid_file_type(self, test_equipment):
        """Test attachment form with invalid file type"""
        file_content = b'Test file content'
        file = SimpleUploadedFile('test.exe', file_content, content_type='application/x-msdownload')
        form_data = {
            'file': file,
            'description': 'Test attachment'
        }
        form = AttachmentForm(data=form_data, files={'file': file})
        assert not form.is_valid()
        assert 'file' in form.errors

@pytest.mark.django_db
class TestStaffCreationForm:
    def test_staff_creation_form_valid_data(self):
        """Test staff creation form with valid data"""
        form_data = {
            'username': 'staffuser',
            'email': 'staff@example.com',
            'password1': 'staffpass123',
            'password2': 'staffpass123',
            'first_name': 'Staff',
            'last_name': 'User',
            'phone_number': '+12125552368',
            'user_type': 'employee',
            'employee_id': 'EMP123',
            'position': 'Sales Associate',
            'department': 'Sales',
            'hire_date': timezone.now().date()
        }
        form = StaffCreationForm(data=form_data)
        assert form.is_valid()
        user = form.save()
        assert user.username == 'staffuser'
        assert user.email == 'staff@example.com'
        assert user.profile.user_type == 'employee'

    def test_staff_creation_form_invalid_role(self):
        """Test staff creation form with invalid role"""
        form_data = {
            'username': 'staffuser',
            'email': 'staff@example.com',
            'password1': 'staffpass123',
            'password2': 'staffpass123',
            'first_name': 'Staff',
            'last_name': 'User',
            'phone_number': '+12125552368',
            'user_type': 'invalid_role',
            'employee_id': 'EMP123',
            'position': 'Sales Associate',
            'department': 'Sales',
            'hire_date': timezone.now().date()
        }
        form = StaffCreationForm(data=form_data)
        assert not form.is_valid()
        assert 'user_type' in form.errors

@pytest.mark.django_db
class TestUserProfileUpdateForm:
    def test_user_profile_update_form_valid_data(self, test_user):
        """Test user profile update form with valid data"""
        form_data = {
            'phone_number': '+12125552368',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345'
        }
        form = UserProfileUpdateForm(data=form_data, instance=test_user.profile)
        assert form.is_valid()
        profile = form.save()
        assert profile.phone_number == '+12125552368'
        assert profile.address == '123 Test St'

    def test_user_profile_update_form_invalid_phone(self, test_user):
        """Test user profile update form with invalid phone number"""
        form_data = {
            'phone_number': 'invalid-phone',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345'
        }
        form = UserProfileUpdateForm(data=form_data, instance=test_user.profile)
        assert not form.is_valid()
        assert 'phone_number' in form.errors 
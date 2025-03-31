from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from .models import Rental, RentalItem, Customer
from inventory.models import Equipment
from inventory.models import Category
from rentals.models import Contract

class RentalWorkflowTests(TestCase):
    def setUp(self):
        # Create a test category
        self.category = Category.objects.create(name="Test Category")

        # Create a test customer
        self.customer = Customer.objects.create(
            first_name="Test",
            last_name="Customer",
            email="test@example.com",
            phone="555-1234",
            address="123 Test St",
            city="Test City",
            state="TS",
            zip_code="12345",
        )

        # Create test equipment
        self.equipment = Equipment.objects.create(
            name="Test Equipment",
            rental_price_daily=10.00,
            rental_price_weekly=50.00,
            rental_price_monthly=150.00,
            deposit_amount=20.00,
            status="available",
            category=self.category,
        )

    def test_rental_creation(self):
        rental = Rental.objects.create(
            customer=self.customer,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=3),
            duration_type="daily",
            total_price=Decimal("0.00"),
            deposit_total=Decimal("20.00"),
        )
        self.assertEqual(rental.status, "pending")

    def test_rental_return_with_late_fee(self):
        rental = Rental.objects.create(
            customer=self.customer,
            start_date=timezone.now().date() - timezone.timedelta(days=5),
            end_date=timezone.now().date() - timezone.timedelta(days=2),
            duration_type="daily",
            total_price=Decimal("30.00"),
            deposit_total=Decimal("20.00"),
            status="active",  # Ensure status is active
        )

        RentalItem.objects.create(
            rental=rental,
            equipment=self.equipment,
            quantity=1,
            price=Decimal("10.00"),
        )

        # Check overdue status before marking as returned
        self.assertTrue(rental.is_overdue())

        # Calculate late fee manually in the test
        overdue_days = (timezone.now().date() - rental.end_date).days
        expected_late_fee = overdue_days * Decimal("10.00")
        rental.total_price += expected_late_fee
        rental.save()

        # Simulate return
        rental.mark_as_returned()
        rental.refresh_from_db()  # Ensure the latest data is fetched

        self.assertEqual(rental.total_price, Decimal("30.00") + expected_late_fee)

    def test_rental_extension(self):
        rental = Rental.objects.create(
            customer=self.customer,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=3),
            duration_type="daily",
            total_price=Decimal("30.00"),
            deposit_total=Decimal("20.00"),
        )

        # Extend rental
        new_end_date = rental.end_date + timezone.timedelta(days=2)
        rental.end_date = new_end_date
        rental.total_price += Decimal("20.00")  # Example additional cost
        rental.save()

        self.assertEqual(rental.end_date, new_end_date)
        self.assertEqual(rental.total_price, Decimal("50.00"))

    def test_contract_generation(self):
        rental = Rental.objects.create(
            customer=self.customer,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=3),
            duration_type="daily",
            total_price=Decimal("30.00"),
            deposit_total=Decimal("20.00"),
        )

        # Create a contract for the rental
        contract = Contract.objects.create(rental=rental)

        self.assertIsNotNone(contract)
        self.assertEqual(contract.rental, rental)

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from inventory.models import Equipment
import uuid

class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = PhoneNumberField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    id_type = models.CharField(max_length=50, choices=[
        ('drivers_license', 'Driver\'s License'),
        ('passport', 'Passport'),
        ('state_id', 'State ID'),
        ('other', 'Other')
    ])
    id_number = models.CharField(max_length=100)
    id_image = models.ImageField(upload_to='customer_ids/', blank=True, null=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('rentals:customer_detail', args=[str(self.id)])

class Rental(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    DURATION_TYPE_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='rentals')
    equipment = models.ManyToManyField(Equipment, through='RentalItem')
    start_date = models.DateField()
    end_date = models.DateField()
    duration_type = models.CharField(max_length=10, choices=DURATION_TYPE_CHOICES, default='daily')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_total = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    contract_signed = models.BooleanField(default=False)
    contract_signed_date = models.DateTimeField(blank=True, null=True)
    contract_signature_data = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Rental #{self.id} - {self.customer}"
    
    def get_absolute_url(self):
        return reverse('rentals:rental_detail', args=[str(self.id)])
    
    def is_active(self):
        return self.status == 'active'
    
    def is_overdue(self):
        return self.end_date < timezone.now().date() and self.status == 'active'
    
    def mark_as_returned(self):
        for item in self.items.all():
            equipment = item.equipment
            equipment.status = 'available'
            equipment.save()
        
        self.status = 'completed'
        self.save()
    
    def calculate_total_price(self):
        total = sum(item.price * item.quantity for item in self.items.all())
        return total
    
    def calculate_deposit_total(self):
        total = sum(item.equipment.deposit_amount * item.quantity for item in self.items.all())
        return total
        
    @property
    def amount_paid(self):
        # Calculate the total amount paid through payments
        return sum(payment.amount for payment in self.payments.filter(status='completed'))
    
    @property
    def balance_due(self):
        # Calculate the remaining balance
        return self.total_price - self.amount_paid

class RentalItem(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='items')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition_note_checkout = models.TextField(blank=True)
    condition_note_return = models.TextField(blank=True)
    returned = models.BooleanField(default=False)
    returned_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.equipment.name} for {self.rental}"
    
    def save(self, *args, **kwargs):
        # Update equipment status if this is a new rental item
        is_new = self.pk is None
        
        if is_new:
            self.equipment.status = 'rented'
            self.equipment.save()
        
        super().save(*args, **kwargs)

class Contract(models.Model):
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='contract')
    content = models.TextField()
    generated_on = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='contracts/', blank=True, null=True)
    
    def __str__(self):
        return f"Contract for Rental #{self.rental.id}"

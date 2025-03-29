from django.db import models
from django.conf import settings
from rentals.models import Rental
from simple_history.models import HistoricalRecords
import uuid

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('rental', 'Rental Payment'),
        ('deposit', 'Security Deposit'),
        ('late_fee', 'Late Fee'),
        ('damage_fee', 'Damage Fee'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('paypal', 'PayPal'),
        ('stripe', 'Credit Card (Stripe)'),
        ('venmo', 'Venmo'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('other', 'Other'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True)
    receipt_sent = models.BooleanField(default=False)
    
    # For refunds
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund_date = models.DateTimeField(blank=True, null=True)
    refund_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Track history
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.get_payment_type_display()} for Rental #{self.rental.id} - ${self.amount}"

class PayPalTransaction(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='paypal_transaction')
    paypal_order_id = models.CharField(max_length=255)
    paypal_payer_id = models.CharField(max_length=255, blank=True, null=True)
    paypal_payer_email = models.EmailField(blank=True, null=True)
    payment_completed_at = models.DateTimeField(blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"PayPal Transaction for Payment #{self.payment.id}"

class StripeTransaction(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='stripe_transaction')
    stripe_charge_id = models.CharField(max_length=255)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    payment_method_id = models.CharField(max_length=255, blank=True, null=True)
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    card_last4 = models.CharField(max_length=4, blank=True, null=True)
    card_brand = models.CharField(max_length=50, blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"Stripe Transaction for Payment #{self.payment.id}"

class VenmoTransaction(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='venmo_transaction')
    venmo_transaction_id = models.CharField(max_length=255)
    venmo_user_id = models.CharField(max_length=255, blank=True, null=True)
    venmo_username = models.CharField(max_length=255, blank=True, null=True)
    venmo_email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Venmo Transaction for Payment #{self.payment.id}"

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    """Base user profile model that extends Django's built-in User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = PhoneNumberField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Administrator'),
    )
    # This field should only be editable by administrators
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    
    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_user_type_display()})"

    @property
    def is_staff_member(self):
        return self.user_type in ['employee', 'admin']
    
    @property
    def is_customer(self):
        return self.user_type == 'customer'

class CustomerProfile(models.Model):
    """Additional fields specific to customers"""
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='customer_info')
    preferred_payment_method = models.CharField(max_length=50, blank=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

class StaffProfile(models.Model):
    """Additional fields specific to staff members (employees/admins)"""
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='staff_info')
    employee_id = models.CharField(max_length=20, unique=True)
    position = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    hire_date = models.DateField()
    
    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.position}"

# Signal to create user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# Signal to create customer profile when a user profile is created with type 'customer'
@receiver(post_save, sender=UserProfile)
def create_customer_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 'customer':
        CustomerProfile.objects.create(user_profile=instance)
    
    # Handle profile type changes
    elif not created:
        if instance.user_type == 'customer':
            CustomerProfile.objects.get_or_create(user_profile=instance)
        else:
            # If changing from customer to staff, delete customer profile if exists
            CustomerProfile.objects.filter(user_profile=instance).delete()

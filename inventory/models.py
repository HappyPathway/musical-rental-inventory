from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
from django.contrib.sites.models import Site
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Equipment(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('maintenance', 'Under Maintenance'),
        ('damaged', 'Damaged'),
        ('retired', 'Retired'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='equipment')
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, unique=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rental_price_daily = models.DecimalField(max_digits=8, decimal_places=2)
    rental_price_weekly = models.DecimalField(max_digits=8, decimal_places=2)
    rental_price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    replacement_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1)
    
    # QR Code related fields
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Manual related fields
    manual_file = models.FileField(upload_to='manuals/', blank=True, null=True)
    manual_title = models.CharField(max_length=255, blank=True, null=True)
    manual_last_checked = models.DateTimeField(blank=True, null=True)
    
    # Media related fields
    main_image = models.ImageField(upload_to='equipment_images/', blank=True, null=True)
    
    # Track history of changes
    history = HistoricalRecords()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.brand})"
    
    def get_absolute_url(self):
        return reverse('inventory:equipment_detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        # Extract and pop our custom parameter before passing to super() method
        skip_qr = kwargs.pop('skip_qr', False)
        skip_manual = kwargs.pop('skip_manual', False)
        
        # Save first to get an ID
        super().save(*args, **kwargs)
        
        # Only generate QR code if:
        # 1. We don't already have one
        # 2. We're not explicitly skipping QR generation
        # 3. We have an ID (needed for QR URL)
        if not self.qr_code and not skip_qr and self.id:
            try:
                self.generate_qr_code()
                # Save again with the QR code, but avoid another full save by specifying update_fields
                super().save(update_fields=['qr_code'])
            except Exception as e:
                # Log the error but don't block saving the equipment
                print(f"Error generating QR code: {e}")
                
        # Fetch manual if needed
        if not skip_manual and self.model_number and not self.manual_file:
            from .utils import download_and_store_manual
            try:
                # This will update the equipment model directly if successful
                download_and_store_manual(self)
                self.manual_last_checked = timezone.now()
                super().save(update_fields=['manual_last_checked'])
            except Exception as e:
                print(f"Error fetching manual: {e}")
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Get the current site's domain
        domain = Site.objects.get_current().domain
        
        # Create the absolute URL with https protocol
        url = f"https://{domain}{reverse('inventory:equipment_detail', args=[str(self.id)])}"
        
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        filename = f'qr-{slugify(self.name)}-{self.qr_uuid}.png'
        self.qr_code.save(filename, File(buffer), save=False)
    
    def is_available(self):
        return self.status == 'available'

    @property
    def quantity_available(self):
        """Return the quantity available for rental."""
        if self.status != 'available':
            return 0
        return self.quantity

class EquipmentAttachment(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='equipment_attachments/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.equipment.name}"

class MaintenanceRecord(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records')
    date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    performed_by = models.CharField(max_length=100, blank=True)
    scheduled_date = models.DateField(blank=True, null=True, help_text="Date when maintenance is scheduled")
    is_completed = models.BooleanField(default=False, help_text="Indicates if the maintenance is completed")

    def __str__(self):
        return f"{self.equipment.name} - {self.date}"

class SearchLog(models.Model):
    """Model to track search queries made by users."""
    query = models.CharField(max_length=255)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='search_logs'
    )
    app = models.CharField(max_length=50, help_text="The app where the search was performed")
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    results_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Search Log'
        verbose_name_plural = 'Search Logs'
    
    def __str__(self):
        return f"{self.query} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class User(AbstractUser):
    """Custom user model for the application."""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = PhoneNumberField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set'
    )

    def __str__(self):
        return self.email

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from simple_history.models import HistoricalRecords
import uuid
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw

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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # QR Code related fields
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
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
        return reverse('inventory:detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        # Generate QR code if it doesn't exist
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"{reverse('inventory:detail', args=[str(self.id)])}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        filename = f'qr-{slugify(self.name)}-{self.qr_uuid}.png'
        self.qr_code.save(filename, File(buffer), save=False)
    
    def is_available(self):
        return self.status == 'available'

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
    
    def __str__(self):
        return f"Maintenance for {self.equipment.name} on {self.date}"

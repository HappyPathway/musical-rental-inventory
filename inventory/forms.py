from django import forms
from .models import Equipment, Category, EquipmentAttachment, MaintenanceRecord
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class EquipmentForm(forms.ModelForm):
    """Form for creating and editing equipment items."""
    
    # We'll handle attachments in the view instead of in the form
    # This avoids the multiple file upload widget issue
    
    class Meta:
        model = Equipment
        fields = [
            'name', 'description', 'category', 'brand', 'model_number', 
            'serial_number', 'purchase_date', 'purchase_price', 'rental_price_daily',
            'rental_price_weekly', 'rental_price_monthly', 'deposit_amount', 
            'status', 'condition', 'notes', 'main_image'
        ]
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'condition': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Make some fields required
        self.fields['name'].required = True
        self.fields['category'].required = True
        self.fields['brand'].required = True
        self.fields['rental_price_daily'].required = True
        self.fields['deposit_amount'].required = True
    
    def clean_serial_number(self):
        """Validate that the serial number is unique if provided."""
        serial_number = self.cleaned_data.get('serial_number')
        
        if not serial_number:
            return serial_number
        
        # Check if this serial number is already in use (exclude current instance if editing)
        instance_id = self.instance.id if self.instance else None
        exists = Equipment.objects.filter(serial_number=serial_number).exclude(id=instance_id).exists()
        
        if exists:
            raise ValidationError(_('Equipment with this serial number already exists.'))
        
        return serial_number

class MobileEquipmentForm(EquipmentForm):
    """A simplified version of the equipment form optimized for mobile devices."""
    
    class Meta(EquipmentForm.Meta):
        fields = [
            'name', 'category', 'brand', 'model_number', 
            'serial_number', 'rental_price_daily', 'deposit_amount', 
            'status', 'condition', 'main_image'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make widgets mobile-friendly
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 2
            field.widget.attrs['class'] = 'form-control mobile-input'

class AttachmentForm(forms.ModelForm):
    """Form for adding attachments to equipment."""
    
    class Meta:
        model = EquipmentAttachment
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 10MB")
            
            # Check file type
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif']
            if file.content_type not in allowed_types:
                raise forms.ValidationError("File type not allowed. Allowed types: PDF, JPEG, PNG, GIF")
            
        return file

class MaintenanceRecordForm(forms.ModelForm):
    """Form for recording maintenance activities."""
    
    class Meta:
        model = MaintenanceRecord
        fields = ['date', 'description', 'cost', 'performed_by']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'performed_by': forms.TextInput(attrs={'class': 'form-control'})
        }
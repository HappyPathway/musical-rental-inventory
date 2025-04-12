from django import forms
from django.utils import timezone
from .models import Customer, Rental, RentalItem
from inventory.models import Equipment

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                  'city', 'state', 'zip_code', 'id_type', 'id_number', 'id_image', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if Customer.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("A customer with this email already exists.")
        return email

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['start_date', 'end_date', 'duration_type', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date()}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.total_price = 0  # Will be calculated after rental items are added
            instance.deposit_total = 0  # Will be calculated after rental items are added
            instance.save()
        return instance

class StaffRentalForm(RentalForm):
    """Rental form for staff users that includes customer selection"""
    class Meta(RentalForm.Meta):
        fields = ['customer'] + RentalForm.Meta.fields

class RentalItemForm(forms.ModelForm):
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(status='available'),
        widget=forms.Select(attrs={'class': 'select2'})
    )
    quantity = forms.IntegerField(
        min_value=1, 
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
    
    class Meta:
        model = RentalItem
        fields = ['equipment', 'quantity']

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 1:
            raise forms.ValidationError("Quantity must be at least 1")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        equipment = cleaned_data.get('equipment')
        quantity = cleaned_data.get('quantity')
        
        if equipment and quantity:
            if equipment.status != 'available':
                raise forms.ValidationError("This equipment is not available for rental")
            if equipment.quantity_available < quantity:
                raise forms.ValidationError(f"Only {equipment.quantity_available} items available")
        
        return cleaned_data

class StaffRentalItemForm(RentalItemForm):
    """RentalItem form for staff users that includes price and condition notes"""
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    condition_note_checkout = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False
    )
    
    class Meta(RentalItemForm.Meta):
        fields = RentalItemForm.Meta.fields + ['price', 'condition_note_checkout']

class EquipmentSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by name, category, or serial number'
    }))
    category = forms.CharField(required=False)
    available_only = forms.BooleanField(required=False, initial=True)

class ReturnRentalItemForm(forms.ModelForm):
    class Meta:
        model = RentalItem
        fields = ['condition_note_return']
        widgets = {
            'condition_note_return': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_condition_note_return(self):
        condition_note = self.cleaned_data.get('condition_note_return')
        if not condition_note:
            raise forms.ValidationError("Please provide a condition note for the returned item")
        return condition_note

class ContractSignatureForm(forms.Form):
    signature = forms.CharField(widget=forms.HiddenInput())
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label="I agree to the terms and conditions of this rental contract"
    )
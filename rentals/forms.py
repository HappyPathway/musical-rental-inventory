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

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['customer', 'start_date', 'end_date', 'duration_type', 'notes']
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
        fields = ['equipment', 'quantity', 'price', 'condition_note_checkout']
        widgets = {
            'condition_note_checkout': forms.Textarea(attrs={'rows': 2}),
        }

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

class ContractSignatureForm(forms.Form):
    signature = forms.CharField(widget=forms.HiddenInput())
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(),
        label="I agree to the terms and conditions of this rental contract"
    )
from django import forms
from .models import Rental, RentalItem, Customer, Contract
from inventory.models import Equipment
from django.forms import ModelForm
from decimal import Decimal

class RentalForm(ModelForm):
    class Meta:
        model = Rental
        fields = ['customer', 'start_date', 'end_date', 'duration_type', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duration_type': forms.Select(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RentalItemForm(forms.Form):
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(status='available'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

class RentalReturnForm(forms.Form):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent - Like New'),
        ('good', 'Good - Minor Wear'),
        ('fair', 'Fair - Noticeable Wear'),
        ('poor', 'Poor - Significant Damage'),
        ('damaged', 'Damaged - Requires Repair')
    ]

    condition = forms.ChoiceField(
        choices=CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    condition_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe any damage or issues...'
        }),
        required=False
    )
    late_fees = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    damage_fees = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=Decimal('0.00'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    refund_deposit = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class RentalExtensionForm(forms.Form):
    new_end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )
    extension_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for extension...'
        }),
        required=False
    )

class ContractForm(forms.Form):
    signature = forms.CharField(
        widget=forms.HiddenInput(attrs={
            'class': 'signature-data'
        })
    )
    
    agree_to_terms = forms.BooleanField(
        label='I agree to the terms and conditions of this rental contract',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
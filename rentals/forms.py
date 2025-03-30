from django import forms
from .models import Rental, RentalItem
from inventory.models import Equipment
from django.forms import ModelForm

class RentalForm(ModelForm):
    class Meta:
        model = Rental
        fields = ['customer', 'start_date', 'end_date', 'duration_type', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RentalItemForm(forms.Form):
    equipment = forms.ModelChoiceField(
        queryset=Equipment.objects.filter(status='available'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
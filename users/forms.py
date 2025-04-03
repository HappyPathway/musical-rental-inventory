from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import UserProfile, CustomerProfile, StaffProfile
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python
from django.core.exceptions import ValidationError

class FlexiblePhoneNumberField(PhoneNumberField):
    """A more flexible phone number field that accepts various formats."""
    
    def to_python(self, value):
        """Convert the input to a proper phone number."""
        if not value:
            return value
            
        # Try to parse the phone number
        phone_number = to_python(value)
        
        if not phone_number:
            # If parsing fails, try to clean up the input and parse again
            cleaned = ''.join(filter(str.isdigit, value))
            if cleaned:
                # If we have digits, try to parse with US region code
                phone_number = to_python('+1' + cleaned)
        
        if not phone_number:
            raise ValidationError('Please enter a valid phone number')
            
        return phone_number

class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with styled fields"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class CustomerRegistrationForm(UserCreationForm):
    """Form for customer registration"""
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_username'}),
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_first_name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_last_name'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email'})
    )
    phone_number = FlexiblePhoneNumberField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_phone_number',
            'placeholder': '(123) 456-7890'
        })
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_address'})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_city'})
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_state'})
    )
    zip_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_zip_code'})
    )
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_agree_to_terms'
        }),
        label="I agree to the Terms and Conditions",
        help_text="You must agree to our Terms and Conditions to create an account."
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'agree_to_terms')
    
    def __init__(self, *args, **kwargs):
        super(CustomerRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password1'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_password2'
        })
        
        # Add labels and help text
        self.fields['username'].label = 'Username'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['email'].label = 'Email Address'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'
        self.fields['phone_number'].label = 'Phone Number'
        self.fields['address'].label = 'Street Address'
        self.fields['city'].label = 'City'
        self.fields['state'].label = 'State'
        self.fields['zip_code'].label = 'ZIP Code'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Create or update profile
            try:
                profile = user.profile
            except Exception:
                # If profile doesn't exist yet, create it
                from .models import UserProfile
                profile = UserProfile.objects.create(user=user)
                
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.city = self.cleaned_data.get('city', '')
            profile.state = self.cleaned_data.get('state', '')
            profile.zip_code = self.cleaned_data.get('zip_code', '')
            profile.user_type = 'customer'
            profile.save()
        
        return user
    
    def signup(self, request, user):
        """Required method for django-allauth integration"""
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Create or update profile
        try:
            profile = user.profile
        except Exception:
            # If profile doesn't exist yet, create it
            from .models import UserProfile
            profile = UserProfile.objects.create(user=user)
            
        profile.phone_number = self.cleaned_data.get('phone_number', '')
        profile.address = self.cleaned_data.get('address', '')
        profile.city = self.cleaned_data.get('city', '')
        profile.state = self.cleaned_data.get('state', '')
        profile.zip_code = self.cleaned_data.get('zip_code', '')
        profile.user_type = 'customer'
        profile.save()
        
        return user

class StaffCreationForm(UserCreationForm):
    """Form for admin to create staff accounts (employees and admins)"""
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone_number = FlexiblePhoneNumberField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(123) 456-7890'
        })
    )
    
    # User type field (employee or admin)
    USER_TYPE_CHOICES = (
        ('employee', 'Employee'),
        ('admin', 'Administrator'),
    )
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Staff specific fields
    employee_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    position = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    department = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    hire_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(StaffCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Set Django's is_staff flag for admin users
        if self.cleaned_data['user_type'] == 'admin':
            user.is_staff = True
        
        if commit:
            user.save()
            # Create or update profile
            try:
                profile = user.profile
            except Exception:
                # If profile doesn't exist yet, create it
                from .models import UserProfile
                profile = UserProfile.objects.create(user=user)
                
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.user_type = self.cleaned_data['user_type']
            profile.save()
            
            # Create or update staff profile
            StaffProfile.objects.update_or_create(
                user_profile=profile,
                defaults={
                    'employee_id': self.cleaned_data['employee_id'],
                    'position': self.cleaned_data['position'],
                    'department': self.cleaned_data['department'],
                    'hire_date': self.cleaned_data['hire_date'],
                }
            )
        
        return user

class UserProfileUpdateForm(ModelForm):
    """Form for users to update their profile information"""
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'city', 'state', 'zip_code')
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(123) 456-7890'
            }),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(ModelForm):
    """Form for users to update their basic information"""
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class AdminUserTypeUpdateForm(ModelForm):
    """Form for administrators to update a user's type/role"""
    class Meta:
        model = UserProfile
        fields = ('user_type',)
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(AdminUserTypeUpdateForm, self).__init__(*args, **kwargs)
        self.fields['user_type'].help_text = "Changing user type may require additional information to be provided."
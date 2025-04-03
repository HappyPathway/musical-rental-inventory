from django import forms
from phonenumber_field.modelfields import PhoneNumberField
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

    def prepare_value(self, value):
        """Convert the phone number to a string for database storage."""
        if not value:
            return value
        return str(value)

    def from_db_value(self, value, expression, connection):
        """Convert the database value to a phone number."""
        if not value:
            return value
        return to_python(value)
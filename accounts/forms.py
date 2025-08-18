from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import CustomUser, UserProfile, Address

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating new users."""
    
    # Additional fields for registration
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254700000000'
        }),
        help_text="Phone number in international format (optional)"
    )
    
    mpesa_number = forms.CharField(
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '254700000000'
        }),
        help_text="M-Pesa phone number (optional)"
    )
    
    # Terms and conditions
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        error_messages={'required': 'You must accept the terms and conditions'}
    )
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'phone_number',
            'mpesa_number', 'password1', 'password2', 'terms_accepted'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize field widgets
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email
    
    def clean_mpesa_number(self):
        """Validate M-Pesa number format."""
        mpesa_number = self.cleaned_data.get('mpesa_number')
        if mpesa_number:
            if not mpesa_number.startswith('254'):
                raise forms.ValidationError('M-Pesa number must start with 254')
            if len(mpesa_number) != 12:
                raise forms.ValidationError('M-Pesa number must be exactly 12 digits')
        return mpesa_number


class CustomUserChangeForm(UserChangeForm):
    """Custom form for changing user information."""
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'phone_number',
            'mpesa_number', 'date_of_birth', 'gender', 'address_line_1',
            'address_line_2', 'city', 'county', 'postal_code'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password field optional
        self.fields['password'].help_text = 'Raw passwords are not stored, so there is no way to see this user\'s password, but you can change the password using <a href="../password/">this form</a>.'


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with better styling."""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    
    class Meta:
        model = UserProfile
        fields = (
            'profile_picture', 'whatsapp', 'facebook', 'instagram', 'twitter',
            'business_name', 'business_description', 'language_preference'
        )
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WhatsApp number'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Facebook profile URL'}),
            'instagram': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instagram username'}),
            'twitter': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Twitter username'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business name'}),
            'business_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'language_preference': forms.Select(attrs={'class': 'form-select'}),
        }


class AddressForm(forms.ModelForm):
    """Form for adding/editing addresses."""
    
    class Meta:
        model = Address
        fields = (
            'address_type', 'recipient_name', 'phone_number', 'address_line_1',
            'address_line_2', 'city', 'county', 'postal_code', 'is_default'
        )
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-select'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name of recipient'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number for delivery'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address, building, etc.'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, unit, etc. (optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'county': forms.Select(attrs={'class': 'form-select'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate county choices with Kenyan counties
        kenya_counties = [
            ('Nairobi', 'Nairobi'),
            ('Mombasa', 'Mombasa'),
            ('Kisumu', 'Kisumu'),
            ('Nakuru', 'Nakuru'),
            ('Eldoret', 'Eldoret'),
            ('Thika', 'Thika'),
            ('Kakamega', 'Kakamega'),
            ('Nyeri', 'Nyeri'),
            ('Machakos', 'Machakos'),
            ('Kisii', 'Kisii'),
            ('Garissa', 'Garissa'),
            ('Wajir', 'Wajir'),
            ('Mandera', 'Mandera'),
            ('Marsabit', 'Marsabit'),
            ('Isiolo', 'Isiolo'),
            ('Meru', 'Meru'),
            ('Embu', 'Embu'),
            ('Kirinyaga', 'Kirinyaga'),
            ('Muranga', 'Muranga'),
            ('Kiambu', 'Kiambu'),
            ('Laikipia', 'Laikipia'),
            ('Nyahururu', 'Nyahururu'),
            ('Narok', 'Narok'),
            ('Kajiado', 'Kajiado'),
            ('Kericho', 'Kericho'),
            ('Bomet', 'Bomet'),
            ('Baringo', 'Baringo'),
            ('Elgeyo Marakwet', 'Elgeyo Marakwet'),
            ('West Pokot', 'West Pokot'),
            ('Samburu', 'Samburu'),
            ('Trans Nzoia', 'Trans Nzoia'),
            ('Uasin Gishu', 'Uasin Gishu'),
            ('Nandi', 'Nandi'),
            ('Vihiga', 'Vihiga'),
            ('Busia', 'Busia'),
            ('Siaya', 'Siaya'),
            ('Homa Bay', 'Homa Bay'),
            ('Migori', 'Migori'),
            ('Kisii', 'Kisii'),
            ('Nyamira', 'Nyamira'),
            ('Bungoma', 'Bungoma'),
            ('Kakamega', 'Kakamega'),
            ('Vihiga', 'Vihiga'),
            ('Taita Taveta', 'Taita Taveta'),
            ('Kwale', 'Kwale'),
            ('Kilifi', 'Kilifi'),
            ('Lamu', 'Lamu'),
            ('Tana River', 'Tana River'),
            ('Kitui', 'Kitui'),
            ('Makueni', 'Makueni'),
            ('Kitui', 'Kitui'),
            ('Machakos', 'Machakos'),
            ('Kajiado', 'Kajiado'),
            ('Narok', 'Narok'),
            ('Nakuru', 'Nakuru'),
            ('Laikipia', 'Laikipia'),
            ('Nyahururu', 'Nyahururu'),
            ('Nyeri', 'Nyeri'),
            ('Kirinyaga', 'Kirinyaga'),
            ('Muranga', 'Muranga'),
            ('Kiambu', 'Kiambu'),
            ('Thika', 'Thika'),
            ('Nairobi', 'Nairobi'),
        ]
        self.fields['county'].choices = [('', 'Select County')] + kenya_counties


class PasswordChangeForm(forms.Form):
    """Form for changing password."""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current password'
        })
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def clean(self):
        """Validate that new passwords match."""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError('New passwords do not match.')
        
        return cleaned_data





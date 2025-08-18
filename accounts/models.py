from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """Custom user model with additional fields for e-commerce."""
    
    # User type choices
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Administrator'),
        ('staff', 'Staff Member'),
    ]
    
    # Gender choices
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    # Additional fields
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text="Phone number in international format"
    )
    
    # M-Pesa number (Kenyan format)
    mpesa_number = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        help_text="M-Pesa phone number (e.g., 254700000000)"
    )
    
    # Profile information
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    
    # Address fields
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return self.email or self.username
    
    def get_full_name(self):
        """Return the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_short_name(self):
        """Return the short name of the user."""
        return self.first_name or self.username


class UserProfile(models.Model):
    """Extended user profile with additional e-commerce specific fields."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    
    # Social media links
    whatsapp = models.CharField(max_length=20, blank=True, help_text="WhatsApp number")
    facebook = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    
    # Business information (for business accounts)
    business_name = models.CharField(max_length=200, blank=True)
    business_description = models.TextField(blank=True)
    business_license = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    
    # Preferences
    language_preference = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('sw', 'Swahili')],
        default='en'
    )
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def get_profile_picture_url(self):
        """Return the profile picture URL or default image."""
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default-profile.png'


class Address(models.Model):
    """User address model for multiple addresses."""
    
    ADDRESS_TYPE_CHOICES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='home')
    
    # Address fields
    recipient_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=17)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True)
    
    # Additional info
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.recipient_name} - {self.address_line_1}, {self.city}"
    
    def save(self, *args, **kwargs):
        """Ensure only one default address per user."""
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)





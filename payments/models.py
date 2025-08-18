from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from simple_history.models import HistoricalRecords
import uuid

User = get_user_model()

class Payment(models.Model):
    """Payment model for tracking all payment transactions."""
    
    # Payment status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Payment method choices
    METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('paypal', 'PayPal'),
        ('flutterwave', 'Flutterwave'),
        ('pesapal', 'Pesapal'),
    ]
    
    # Payment information
    payment_id = models.CharField(max_length=50, unique=True, blank=True)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction details
    transaction_id = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=200, blank=True)
    
    # Payment gateway response
    gateway_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        """Auto-generate payment ID if not provided."""
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def mark_as_completed(self):
        """Mark payment as completed."""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def mark_as_failed(self, error_message=""):
        """Mark payment as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
    
    def get_status_display_class(self):
        """Get CSS class for status display."""
        status_classes = {
            'pending': 'badge-warning',
            'processing': 'badge-info',
            'completed': 'badge-success',
            'failed': 'badge-danger',
            'cancelled': 'badge-secondary',
            'refunded': 'badge-info',
        }
        return status_classes.get(self.status, 'badge-secondary')


class MpesaPayment(models.Model):
    """M-Pesa specific payment model."""
    
    # M-Pesa transaction status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='mpesa_details')
    
    # M-Pesa specific fields
    phone_number = models.CharField(max_length=12, help_text="M-Pesa phone number (e.g., 254700000000)")
    checkout_request_id = models.CharField(max_length=100, blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    
    # Transaction details
    business_shortcode = models.CharField(max_length=10, blank=True)
    account_reference = models.CharField(max_length=100, blank=True)
    transaction_description = models.CharField(max_length=100, blank=True)
    
    # M-Pesa response
    result_code = models.CharField(max_length=10, blank=True)
    result_description = models.TextField(blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'M-Pesa Payment'
        verbose_name_plural = 'M-Pesa Payments'
    
    def __str__(self):
        return f"M-Pesa Payment for {self.payment.payment_id}"
    
    def get_phone_display(self):
        """Format phone number for display."""
        if self.phone_number.startswith('254'):
            return f"+{self.phone_number}"
        return self.phone_number


class CardPayment(models.Model):
    """Credit/Debit card payment model."""
    
    # Card payment status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='card_details')
    
    # Card information (masked)
    last_four_digits = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    expiry_month = models.CharField(max_length=2, blank=True)
    expiry_year = models.CharField(max_length=4, blank=True)
    
    # Payment gateway details
    gateway_name = models.CharField(max_length=50, blank=True)
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    authorization_code = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Card Payment'
        verbose_name_plural = 'Card Payments'
    
    def __str__(self):
        return f"Card Payment for {self.payment.payment_id}"
    
    def get_card_display(self):
        """Get masked card number for display."""
        if self.last_four_digits:
            return f"**** **** **** {self.last_four_digits}"
        return "**** **** **** ****"


class PaymentMethod(models.Model):
    """Available payment methods configuration."""
    
    # Payment method types
    METHOD_TYPES = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('paypal', 'PayPal'),
        ('flutterwave', 'Flutterwave'),
        ('pesapal', 'Pesapal'),
    ]
    
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES, unique=True)
    description = models.TextField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    
    # Settings
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    processing_fee_type = models.CharField(
        max_length=10,
        choices=[('fixed', 'Fixed Amount'), ('percentage', 'Percentage')],
        default='fixed'
    )
    
    # Gateway configuration
    gateway_config = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name
    
    def calculate_processing_fee(self, amount):
        """Calculate processing fee for given amount."""
        if self.processing_fee_type == 'percentage':
            return (amount * self.processing_fee) / 100
        return self.processing_fee
    
    def is_available_for_amount(self, amount):
        """Check if payment method is available for given amount."""
        if amount < self.minimum_amount:
            return False
        if self.maximum_amount and amount > self.maximum_amount:
            return False
        return True


class Refund(models.Model):
    """Payment refund model."""
    
    # Refund status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Refund reason choices
    REASON_CHOICES = [
        ('customer_request', 'Customer Request'),
        ('duplicate_payment', 'Duplicate Payment'),
        ('fraudulent', 'Fraudulent Transaction'),
        ('product_return', 'Product Return'),
        ('technical_error', 'Technical Error'),
        ('other', 'Other'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Processing details
    refund_reference = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Admin information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund for Payment {self.payment.payment_id} - {self.amount}"
    
    def get_status_display_class(self):
        """Get CSS class for status display."""
        status_classes = {
            'pending': 'badge-warning',
            'processing': 'badge-info',
            'completed': 'badge-success',
            'failed': 'badge-danger',
            'cancelled': 'badge-secondary',
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def mark_as_completed(self):
        """Mark refund as completed."""
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at'])


class PaymentGateway(models.Model):
    """Payment gateway configuration model."""
    
    # Gateway types
    GATEWAY_TYPES = [
        ('stripe', 'Stripe'),
        ('mpesa', 'M-Pesa'),
        ('flutterwave', 'Flutterwave'),
        ('pesapal', 'Pesapal'),
        ('paypal', 'PayPal'),
        ('custom', 'Custom Gateway'),
    ]
    
    name = models.CharField(max_length=100)
    gateway_type = models.CharField(max_length=20, choices=GATEWAY_TYPES)
    description = models.TextField(blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    
    # API credentials
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    webhook_secret = models.CharField(max_length=500, blank=True)
    
    # Gateway settings
    gateway_config = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.gateway_type})"
    
    def get_config_value(self, key, default=None):
        """Get configuration value from gateway_config."""
        return self.gateway_config.get(key, default)
    
    def set_config_value(self, key, value):
        """Set configuration value in gateway_config."""
        self.gateway_config[key] = value
        self.save(update_fields=['gateway_config'])


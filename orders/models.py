from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.urls import reverse
from simple_history.models import HistoricalRecords
import uuid
from django.conf import settings
from django.utils import timezone

User = get_user_model()

class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_price(self):
        return self.quantity * self.price

    def get_total_price(self):
        return self.quantity * self.price
        
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

class Order(models.Model):
    """Consolidated Order model combining both versions"""
    
    # Order status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Payment status choices
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # Payment method choices
    PAYMENT_METHODS = [
        ('MPESA', 'M-Pesa'),
        ('CARD', 'Credit Card'),
        ('PAYPAL', 'PayPal'),
    ]
    
    # Order information
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True)
    
    # Customer information
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=17)
    
    # Address information
    shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)
    billing_address_line_1 = models.CharField(max_length=255)
    billing_address_line_2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_county = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=10, blank=True)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping information
    shipping_method = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    payment_reference = models.CharField(max_length=200, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Notes
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # History tracking
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        """Auto-generate order number if not provided."""
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.pk})
    
    def get_status_display_class(self):
        status_classes = {
            'pending': 'badge-warning',
            'confirmed': 'badge-info',
            'processing': 'badge-primary',
            'shipped': 'badge-info',
            'delivered': 'badge-success',
            'cancelled': 'badge-danger',
            'refunded': 'badge-secondary',
        }
        return status_classes.get(self.status, 'badge-secondary')
    
    def calculate_totals(self):
        self.subtotal = sum(item.get_total_price() for item in self.items.all())
        self.total_amount = self.subtotal + self.shipping_cost + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'total_amount'])
    
    def is_eligible_for_return(self):
        if not self.delivery_date:
            return False
        return (self.status == 'delivered' and 
               (timezone.now() - self.delivery_date).days <= 14)

    def get_total(self):
        """Safely return the order total, computing if missing."""
        if self.total_amount is None or self.subtotal is None:
            self.calculate_totals()
        return self.total_amount

class Address(models.Model):
    """Address model for shipping/billing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=[('shipping', 'Shipping'), ('billing', 'Billing')])
    line_1 = models.CharField(max_length=255)
    line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.line_1}, {self.city}"

class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'), 
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
    ]
    
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    preferred_refund_method = models.CharField(
        max_length=50,
        choices=[('store_credit', 'Store Credit'),
                 ('bank_transfer', 'Bank Transfer')],
        default='store_credit'
    )
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Return #{self.id} for Order #{self.order.id}"
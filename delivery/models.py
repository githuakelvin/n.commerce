from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

class ShippingZone(models.Model):
    """Model representing a shipping zone/region"""
    name = models.CharField(_('zone name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    price = models.DecimalField(
        _('shipping price'), 
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    estimated_delivery_time = models.CharField(
        _('estimated delivery time'), 
        max_length=50,
        help_text=_('e.g., 2-3 business days')
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('shipping zone')
        verbose_name_plural = _('shipping zones')
        ordering = ['name']

    def __str__(self):
        return self.name


class PickupPoint(models.Model):
    """Model representing a pickup location for orders"""
    name = models.CharField(_('location name'), max_length=100)
    address = models.CharField(_('address'), max_length=255)
    city = models.CharField(_('city'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    country = models.CharField(_('country'), max_length=100, default='Kenya')
    contact_number = models.CharField(_('contact number'), max_length=20)
    operating_hours = models.CharField(
        _('operating hours'), 
        max_length=100,
        help_text=_('e.g., Mon-Fri 9am-5pm')
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('pickup point')
        verbose_name_plural = _('pickup points')
        ordering = ['city', 'name']

    def __str__(self):
        return f"{self.name} ({self.city})"


class DeliveryStatus(models.Model):
    """Model to track delivery status history"""
    STATUS_CHOICES = [
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('in_transit', _('In Transit')),
        ('out_for_delivery', _('Out for Delivery')),
        ('delivered', _('Delivered')),
        ('returned', _('Returned')),
        ('failed', _('Delivery Failed')),
    ]

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='delivery_statuses',
        verbose_name=_('order')
    )
    status = models.CharField(
        _('status'), 
        max_length=20, 
        choices=STATUS_CHOICES
    )
    location = models.CharField(_('location'), max_length=100)
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(_('date/time'), auto_now_add=True)

    class Meta:
        verbose_name = _('delivery status')
        verbose_name_plural = _('delivery statuses')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_status_display()} - {self.location} ({self.created_at})"
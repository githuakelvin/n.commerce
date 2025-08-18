from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ShippingZone, PickupPoint, DeliveryStatus

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'price_display',
        'estimated_delivery_time',
        'is_active',
        'created_at',
        'actions'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Pricing & Delivery', {
            'fields': ('price', 'estimated_delivery_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_display(self, obj):
        return f"KSh {obj.price:.2f}"
    price_display.short_description = 'Shipping Price'
    price_display.admin_order_field = 'price'

    def actions(self, obj):
        return format_html(
            '<a href="{}" class="button">Edit</a>&nbsp;'
            '<a href="{}" class="button">View</a>',
            reverse('admin:shipping_shippingzone_change', args=[obj.id]),
            reverse('admin:shipping_shippingzone_detail', args=[obj.id])
        )
    actions.short_description = 'Actions'

@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'city_country',
        'contact_number',
        'operating_hours_short',
        'is_active',
        'actions'
    )
    list_filter = ('is_active', 'city', 'country')
    search_fields = ('name', 'address', 'city', 'contact_number')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active')
        }),
        ('Location Details', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Contact & Hours', {
            'fields': ('contact_number', 'operating_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def city_country(self, obj):
        return f"{obj.city}, {obj.country}"
    city_country.short_description = 'Location'
    city_country.admin_order_field = 'city'

    def operating_hours_short(self, obj):
        return obj.operating_hours[:20] + '...' if len(obj.operating_hours) > 20 else obj.operating_hours
    operating_hours_short.short_description = 'Operating Hours'

    def actions(self, obj):
        return format_html(
            '<a href="{}" class="button">Edit</a>&nbsp;'
            '<a href="{}" class="button">View</a>',
            reverse('admin:shipping_pickuppoint_change', args=[obj.id]),
            reverse('admin:shipping_pickuppoint_detail', args=[obj.id])
        )
    actions.short_description = 'Actions'

@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = (
        'order_link',
        'status_badge',
        'location',
        'created_at',
        'notes_short'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'location', 'notes')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Delivery Information', {
            'fields': ('order', 'status', 'location')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Order #{}</a>', url, obj.order.id)
    order_link.short_description = 'Order'

    def status_badge(self, obj):
        status_classes = {
            'processing': 'badge-secondary',
            'shipped': 'badge-info',
            'in_transit': 'badge-primary',
            'out_for_delivery': 'badge-warning',
            'delivered': 'badge-success',
            'returned': 'badge-danger',
            'failed': 'badge-dark',
        }
        return format_html(
            '<span class="badge {}">{}</span>',
            status_classes.get(obj.status, 'badge-secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def notes_short(self, obj):
        return obj.notes[:50] + '...' if obj.notes and len(obj.notes) > 50 else obj.notes or '-'
    notes_short.short_description = 'Notes'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')
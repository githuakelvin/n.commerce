from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.apps import apps

# Get user model safely
User = get_user_model()

def get_order_model():
    return apps.get_model('orders', 'Order')

def get_address_model():
    return apps.get_model('orders', 'Address')

def get_returnrequest_model():
    return apps.get_model('orders', 'ReturnRequest')

def get_orderitem_model():
    return apps.get_model('orders', 'OrderItem')

class OrderItemInline(admin.TabularInline):
    model = get_orderitem_model()
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_price')
    fields = ('product', 'quantity', 'price', 'total_price')

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(get_address_model())
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'line_1', 'city', 'county', 'is_default')
    list_filter = ('address_type', 'city', 'county', 'is_default')
    search_fields = ('user__email', 'line_1', 'city', 'postal_code')
    list_editable = ('is_default',)
    list_select_related = ('user',)

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'address_type', 'is_default')
        }),
        ('Address Details', {
            'fields': ('line_1', 'line_2', 'city', 'county', 'postal_code')
        }),
    )

@admin.register(get_order_model())
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    admin_actions_list = [  # Renamed from 'actions' to avoid conflict
        'mark_as_confirmed',
        'mark_as_processing',
        'mark_as_shipped',
        'mark_as_delivered',
        'mark_as_cancelled',
        'generate_shipping_label'
    ]
    
    list_display = (
        'order_number',
        'customer_display',
        'status_badge',
        'payment_status_badge',
        'total_amount',
        'created_at',
        'action_buttons'  # Consistent naming for the display method
    )
    
    def get_actions(self, request):
        # Map the renamed actions list to Django's expected 'actions'
        actions = super().get_actions(request)
        for action in self.admin_actions_list:
            actions[action] = (
                getattr(self, action),
                action,
                getattr(getattr(self, action), 'short_description', action)
            )
        return actions
    
    def action_buttons(self, obj):
        return format_html(
            '<div class="btn-group">'
            '<a href="{}" class="btn btn-sm btn-info">View</a>'
            '<a href="{}" class="btn btn-sm btn-warning">Edit</a>'
            '</div>',
            reverse('admin:orders_order_change', args=[obj.id]),
            reverse('admin:orders_order_change', args=[obj.id])
        )
    action_buttons.short_description = 'Actions'

    # Keep all your existing action methods (mark_as_confirmed, etc.)
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f"{updated} orders marked as Confirmed")
    mark_as_confirmed.short_description = "Mark selected as Confirmed"

    # ... [keep all other action methods unchanged] ...

@admin.register(get_returnrequest_model())
class ReturnRequestAdmin(admin.ModelAdmin):
    admin_actions_list = [  # Renamed from 'actions'
        'approve_returns',
        'reject_returns',
        'complete_returns'
    ]
    
    list_display = (
        'id',
        'order_link',
        'user_link',
        'status_badge',
        'preferred_refund_method',
        'created_at',
        'action_buttons'  # Consistent naming
    )
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        for action in self.admin_actions_list:
            actions[action] = (
                getattr(self, action),
                action,
                getattr(getattr(self, action), 'short_description', action)
            )
        return actions
    
    def action_buttons(self, obj):
        return format_html(
            '<div class="btn-group">'
            '<a href="{}" class="btn btn-sm btn-info">View</a>'
            '<a href="{}" class="btn btn-sm btn-warning">Edit</a>'
            '</div>',
            reverse('admin:orders_returnrequest_change', args=[obj.id]),
            reverse('admin:orders_returnrequest_change', args=[obj.id])
        )
    action_buttons.short_description = 'Actions'

    # Keep all your existing action methods
    def approve_returns(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved')
        self.message_user(request, f"{updated} returns approved", messages.SUCCESS)
    approve_returns.short_description = "Approve selected returns"

    # ... [keep other action methods unchanged] ...
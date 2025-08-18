from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserProfile, Address

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin interface for CustomUser model."""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'county')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number', 'mpesa_number',
                'date_of_birth', 'gender', 'user_type'
            )
        }),
        ('Address', {
            'fields': (
                'address_line_1', 'address_line_2', 'city', 'county', 'postal_code'
            )
        }),
        ('Preferences', {
            'fields': (
                'newsletter_subscription', 'marketing_emails', 'sms_notifications'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 'user_type',
                'first_name', 'last_name', 'phone_number'
            ),
        }),
    )
    
    def get_queryset(self, request):
        """Custom queryset with select_related for better performance."""
        return super().get_queryset(request).select_related('profile')
    
    def get_phone_display(self, obj):
        """Display phone number with formatting."""
        if obj.phone_number:
            return format_html('<span style="font-family: monospace;">{}</span>', obj.phone_number)
        return '-'
    get_phone_display.short_description = 'Phone Number'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model."""
    
    list_display = ('user', 'business_name', 'language_preference', 'two_factor_enabled', 'created_at')
    list_filter = ('language_preference', 'two_factor_enabled', 'created_at')
    search_fields = ('user__username', 'user__email', 'business_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Profile Picture', {'fields': ('profile_picture',)}),
        ('Social Media', {
            'fields': ('whatsapp', 'facebook', 'instagram', 'twitter')
        }),
        ('Business Information', {
            'fields': ('business_name', 'business_description', 'business_license', 'tax_id')
        }),
        ('Preferences', {'fields': ('language_preference',)}),
        ('Security', {'fields': ('two_factor_enabled', 'last_login_ip')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Custom queryset with select_related for better performance."""
        return super().get_queryset(request).select_related('user')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin interface for Address model."""
    
    list_display = ('user', 'recipient_name', 'address_type', 'city', 'county', 'is_default', 'is_active')
    list_filter = ('address_type', 'county', 'city', 'is_default', 'is_active', 'created_at')
    search_fields = ('user__username', 'recipient_name', 'address_line_1', 'city', 'county')
    ordering = ('-is_default', '-created_at')
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Address Information', {
            'fields': (
                'address_type', 'recipient_name', 'phone_number',
                'address_line_1', 'address_line_2', 'city', 'county', 'postal_code'
            )
        }),
        ('Status', {'fields': ('is_default', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        """Custom queryset with select_related for better performance."""
        return super().get_queryset(request).select_related('user')
    
    def save_model(self, request, obj, form, change):
        """Custom save logic to handle default address."""
        if obj.is_default:
            # Set all other addresses for this user to non-default
            Address.objects.filter(user=obj.user, is_default=True).exclude(pk=obj.pk).update(is_default=False)
        super().save_model(request, obj, form, change)




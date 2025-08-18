from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, MpesaPayment, CardPayment, PaymentMethod, Refund, PaymentGateway

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    list_editable = ('is_active',)
    ordering = ('name',)

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'test_mode', 'created_at')
    list_filter = ('is_active', 'test_mode')
    search_fields = ('name',)
    list_editable = ('is_active', 'test_mode')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'user_link', 'amount', 'method', 'status', 'created_at')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('order__id', 'user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed', 'mark_as_failed']

    def order_link(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">{}</a>', obj.order.id, obj.order)
    order_link.short_description = 'Order'

    def user_link(self, obj):
        return format_html('<a href="/admin/auth/user/{}/change/">{}</a>', obj.user.id, obj.user)
    user_link.short_description = 'User'

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} payments marked as completed.")
    mark_as_completed.short_description = "Mark selected payments as completed"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f"{updated} payments marked as failed.")
    mark_as_failed.short_description = "Mark selected payments as failed"

@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_link', 'phone_number', 'status', 'checkout_request_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('payment__order__id', 'phone_number', 'checkout_request_id')
    readonly_fields = ('created_at', 'updated_at')

    def payment_link(self, obj):
        return format_html('<a href="/admin/payments/payment/{}/change/">{}</a>', obj.payment.id, obj.payment)
    payment_link.short_description = 'Payment'

@admin.register(CardPayment)
class CardPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_link', 'status', 'card_brand', 'last_four_digits', 'gateway_transaction_id', 'created_at')
    list_filter = ('status', 'card_brand')
    search_fields = ('payment__order__id', 'gateway_transaction_id', 'last_four_digits')
    readonly_fields = ('created_at', 'updated_at')

    def payment_link(self, obj):
        return format_html('<a href="/admin/payments/payment/{}/change/">{}</a>', obj.payment.id, obj.payment)
    payment_link.short_description = 'Payment'

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_link', 'order_link', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('payment__order__id', 'payment__id')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_refunds', 'reject_refunds']

    def payment_link(self, obj):
        return format_html('<a href="/admin/payments/payment/{}/change/">{}</a>', obj.payment.id, obj.payment)
    payment_link.short_description = 'Payment'

    def order_link(self, obj):
        return format_html('<a href="/admin/orders/order/{}/change/">{}</a>', obj.order.id, obj.order)
    order_link.short_description = 'Order'

    def approve_refunds(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} refunds approved.")
    approve_refunds.short_description = "Approve selected refunds"

    def reject_refunds(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f"{updated} refunds rejected.")
    reject_refunds.short_description = "Reject selected refunds"
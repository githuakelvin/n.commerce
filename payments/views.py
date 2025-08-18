from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.conf import settings
from .models import (
    Payment, 
    MpesaPayment, 
    CardPayment, 
    PaymentMethod, 
    Refund,
    PaymentGateway
)
from orders.models import Order
import json
import requests
from datetime import datetime

@login_required
def initiate_payment(request, order_id):
    """View to initiate a payment for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        amount = order.get_total()
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=amount,
            method=payment_method,
            status='pending'
        )
        
        # Handle different payment methods
        if payment_method == 'mpesa':
            return initiate_mpesa_payment(request, payment_id=payment.id)
        elif payment_method == 'card':
            return initiate_card_payment(request, payment_id=payment.id)
        else:
            messages.error(request, "Selected payment method is not available")
            return redirect('orders:order_detail', pk=order.id)
    
    # GET request - show payment method selection
    available_methods = PaymentMethod.objects.filter(is_active=True)
    context = {
        'order': order,
        'payment_methods': available_methods
    }
    return render(request, 'payments/payment_methods.html', context)

def initiate_mpesa_payment(request, payment_id=None):
    """Handle M-Pesa payment initiation"""
    # Support both internal calls (with payment_id) and direct URL calls
    if isinstance(payment_id, int) or (isinstance(payment_id, str) and payment_id.isdigit()):
        payment = get_object_or_404(Payment, id=payment_id)
    else:
        # Backward compatibility if called with keyword 'payment'
        payment = payment_id if isinstance(payment_id, Payment) else None
        if payment is None:
            return redirect('payments:payment_failed', payment_id=payment_id)
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        # Create M-Pesa payment record
        mpesa_payment = MpesaPayment.objects.create(
            payment=payment,
            phone_number=phone_number,
            status='pending'
        )
        
        # Call M-Pesa API (example implementation)
        try:
            response = call_mpesa_stk_push(
                phone_number,
                payment.amount,
                f"Order {payment.order.id}",
                f"PAY-{payment.id}"
            )
            
            if response.get('ResponseCode') == '0':
                mpesa_payment.checkout_request_id = response.get('CheckoutRequestID')
                mpesa_payment.merchant_request_id = response.get('MerchantRequestID')
                mpesa_payment.status = 'initiated'
                mpesa_payment.save()
                
                payment.status = 'processing'
                payment.save()
                
                messages.success(request, "M-Pesa payment request sent to your phone")
                return redirect('payments:payment_status', payment_id=payment.id)
            else:
                payment.mark_as_failed(response.get('ResponseDescription'))
                messages.error(request, "Failed to initiate M-Pesa payment")
                return redirect('orders:order_detail', pk=payment.order.id)
                
        except Exception as e:
            payment.mark_as_failed(str(e))
            messages.error(request, "Payment processing failed")
            return redirect('orders:order_detail', pk=payment.order.id)
    
    # GET request - show M-Pesa payment form
    return render(request, 'payments/mpesa_payment.html', {'payment': payment})

def initiate_card_payment(request, payment_id=None):
    """Handle card payment initiation"""
    if isinstance(payment_id, int) or (isinstance(payment_id, str) and payment_id.isdigit()):
        payment = get_object_or_404(Payment, id=payment_id)
    else:
        payment = payment_id if isinstance(payment_id, Payment) else None
        if payment is None:
            return redirect('payments:payment_failed', payment_id=payment_id)
    if request.method == 'POST':
        # In a real implementation, you would:
        # 1. Get token from payment processor (Stripe, etc)
        # 2. Create payment record
        # 3. Process payment
        
        try:
            # Example implementation with Stripe
            card_payment = CardPayment.objects.create(
                payment=payment,
                status='pending'
            )
            
            # Process payment (pseudo-code)
            payment_intent = create_stripe_payment_intent(
                amount=payment.amount,
                currency=payment.currency,
                payment_method_id=request.POST.get('payment_method_id'),
                metadata={
                    'order_id': payment.order.id,
                    'payment_id': payment.id
                }
            )
            
            if payment_intent.status == 'succeeded':
                card_payment.status = 'captured'
                card_payment.gateway_transaction_id = payment_intent.id
                card_payment.last_four_digits = payment_intent.payment_method.card.last4
                card_payment.card_brand = payment_intent.payment_method.card.brand
                card_payment.save()
                
                payment.mark_as_completed()
                messages.success(request, "Payment completed successfully")
                return redirect('payments:payment_success', payment_id=payment.id)
            else:
                payment.mark_as_failed("Payment authorization failed")
                messages.error(request, "Payment authorization failed")
                return redirect('payments:payment_failed', payment_id=payment.id)
                
        except Exception as e:
            payment.mark_as_failed(str(e))
            messages.error(request, "Payment processing failed")
            return redirect('orders:order_detail', pk=payment.order.id)
    
    # GET request - show card payment form
    context = {
        'payment': payment,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')
    }
    return render(request, 'payments/card_payment.html', context)

@login_required
def payment_status(request, payment_id):
    """View to check payment status"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # For AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': payment.status,
            'status_display': payment.get_status_display(),
            'is_completed': payment.status == 'completed'
        })
    
    context = {
        'payment': payment,
        'order': payment.order
    }
    
    # Add payment method specific details
    if payment.method == 'mpesa' and hasattr(payment, 'mpesa_details'):
        context['mpesa_payment'] = payment.mpesa_details
    elif payment.method == 'card' and hasattr(payment, 'card_details'):
        context['card_payment'] = payment.card_details
    
    return render(request, 'payments/payment_status.html', context)

@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payments/payment_success.html', {'payment': payment})

@login_required
def payment_failed(request, payment_id):
    """Payment failed page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payments/payment_failed.html', {'payment': payment})

@login_required
def request_refund(request, payment_id):
    """View for customers to request refunds"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
        description = request.POST.get('description', '')
        
        # Create refund request
        refund = Refund.objects.create(
            payment=payment,
            order=payment.order,
            amount=payment.amount,
            reason=reason,
            description=description,
            status='pending'
        )
        
        messages.success(request, "Refund request submitted successfully")
        return redirect('payments:refund_detail', refund_id=refund.id)
    
    return render(request, 'payments/request_refund.html', {'payment': payment})

@login_required
def refund_detail(request, refund_id):
    """View refund details"""
    refund = get_object_or_404(Refund, id=refund_id, payment__user=request.user)
    return render(request, 'payments/refund_detail.html', {'refund': refund})

class PaymentHistoryView(ListView):
    """View for user's payment history"""
    model = Payment
    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')

class PaymentDetailView(DetailView):
    """View for payment details"""
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

# Helper functions for payment processing
def call_mpesa_stk_push(phone_number, amount, description, reference):
    """Example M-Pesa STK push implementation"""
    # This is a mock implementation - replace with actual M-Pesa API calls
    # In production, you would use the Safaricom API or a library like django-mpesa
    
    # Example response structure
    return {
        "ResponseCode": "0",
        "ResponseDescription": "Success",
        "MerchantRequestID": "WALLET_123456789",
        "CheckoutRequestID": "ws_CO_123456789",
        "CustomerMessage": "Please enter your M-Pesa PIN to complete payment"
    }

def create_stripe_payment_intent(amount, currency, payment_method_id, metadata):
    """Example Stripe payment intent creation"""
    # This is a mock implementation - replace with actual Stripe API calls
    # In production, you would use the Stripe Python library
    
    # Example response structure
    return type('obj', (object,), {
    'status': 'succeeded',
    'id': 'pi_123456789',
    'payment_method': type('obj', (object,), {
        'card': type('obj', (object,), {
            'last4': '4242',
            'brand': 'visa'
        })
    })
})
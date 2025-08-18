from django.shortcuts import render
# Example view (modify as needed)
def order_list(request):
    return render(request, 'orders/order_list.html')

from django.shortcuts import render, redirect
from django.contrib import messages

def checkout(request):
    if request.method == 'POST':
        # Process the order (add your logic here)
        messages.success(request, "Order placed successfully!")
        return redirect('order_confirmation')  # Redirect to a success page
    else:
        return render(request, 'orders/checkout.html')  # Render the checkout form

def shipping_info(request):
    # Your shipping information handling logic here
    return render(request, 'orders/shipping_info.html')


def payment_info(request):
    if request.method == 'POST':
        # Process payment information
        payment_method = request.POST.get('payment_method')
        # Add your payment processing logic here
        messages.success(request, "Payment information saved successfully!")
        return redirect('checkout')  # Redirect to checkout or order confirmation
        
    # Default GET request handling
    context = {
        'payment_methods': [
            {'value': 'credit_card', 'label': 'Credit Card'},
            {'value': 'mpesa', 'label': 'M-Pesa'},
            {'value': 'paypal', 'label': 'PayPal'},
        ]
    }
    return render(request, 'orders/payment_info.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order  # Assuming you have an Order model

@login_required
def order_confirmation(request):
    # Get the most recent order for the current user
    order = get_object_or_404(Order, user=request.user, ordered=False).order_by('-created_at').first()
    
    if not order:
        # Handle case where no order exists
        return render(request, 'orders/no_order.html')
    
    # Mark order as completed (pseudo-code - adjust to your logic)
    order.ordered = True
    order.save()
    
    context = {
        'order': order,
        'order_items': order.items.all(),  # Assuming items relationship
        'delivery_date': order.created_at.date(),  # Example delivery estimate
        'tracking_number': order.generate_tracking_number(),  # If you have this method
    }
    return render(request, 'orders/order_confirmation.html', context)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    context = {
        'order': order,
        'order_items': order.items.all(),
        'can_cancel': order.status in ['PENDING', 'PROCESSING'],
        'status_classes': {
            'PENDING': 'badge-secondary',
            'PROCESSING': 'badge-info',
            'SHIPPED': 'badge-primary',
            'DELIVERED': 'badge-success',
            'CANCELLED': 'badge-danger',
        }
    }
    return render(request, 'orders/order_detail.html', context)

@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    if request.method == 'POST':
        if order.status in ['PENDING', 'PROCESSING']:
            order.status = 'CANCELLED'
            order.save()
            messages.success(request, f"Order #{order.id} has been cancelled successfully.")
            # Add refund logic here if needed
        else:
            messages.error(request, "This order cannot be cancelled at this stage.")
        return redirect('order_detail', pk=order.id)
    
    return render(request, 'orders/cancel_order.html', {'order': order})

@login_required
def track_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    # Sample tracking data - replace with your actual tracking logic
    tracking_events = [
        {
            'status': 'ORDER_PLACED',
            'date': order.created_at,
            'location': 'Nairobi',
            'description': 'Order received',
            'completed': True
        },
        {
            'status': 'PROCESSING',
            'date': order.created_at.replace(hour=order.created_at.hour+1),
            'location': 'Nairobi',
            'description': 'Order being processed',
            'completed': order.status in ['PROCESSING', 'SHIPPED', 'DELIVERED']
        },
        {
            'status': 'SHIPPED',
            'date': order.created_at.replace(day=order.created_at.day+1),
            'location': 'Nairobi',
            'description': 'Order shipped',
            'completed': order.status in ['SHIPPED', 'DELIVERED']
        },
        {
            'status': 'DELIVERED',
            'date': order.created_at.replace(day=order.created_at.day+3),
            'location': request.user.profile.city if hasattr(request.user, 'profile') else 'Your location',
            'description': 'Order delivered',
            'completed': order.status == 'DELIVERED'
        }
    ]
    
    context = {
        'order': order,
        'tracking_events': tracking_events,
        'current_status': order.status
    }
    return render(request, 'orders/track_order.html', context)

from django.core.paginator import Paginator

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination - 10 orders per page
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Status badge classes
    status_classes = {
        'PENDING': 'badge-secondary',
        'PROCESSING': 'badge-info',
        'SHIPPED': 'badge-primary',
        'DELIVERED': 'badge-success',
        'CANCELLED': 'badge-danger',
    }
    
    context = {
        'page_obj': page_obj,
        'status_classes': status_classes,
        'orders_count': orders.count(),
    }
    return render(request, 'orders/order_list.html', context)

    from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ReturnRequestForm

@login_required
def order_history(request):
    # Get all delivered orders
    orders = Order.objects.filter(
        user=request.user,
        status='DELIVERED'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'history_count': orders.count(),
    }
    return render(request, 'orders/order_history.html', context)

@login_required
def create_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if order is eligible for return (delivered within last 14 days)
    if not order.is_eligible_for_return():
        messages.error(request, "This order is not eligible for return")
        return redirect('order_detail', pk=order.id)
    
    # Check if return already exists
    if ReturnRequest.objects.filter(order=order).exists():
        messages.info(request, "You've already requested a return for this order")
        return redirect('return_detail', pk=ReturnRequest.objects.get(order=order).id)
    
    if request.method == 'POST':
        form = ReturnRequestForm(request.POST)
        if form.is_valid():
            return_request = form.save(commit=False)
            return_request.order = order
            return_request.user = request.user
            return_request.save()
            messages.success(request, "Return request submitted successfully!")
            return redirect('return_detail', pk=return_request.id)
    else:
        form = ReturnRequestForm()
    
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'orders/create_return.html', context)

@login_required
def return_list(request):
    returns = ReturnRequest.objects.filter(
        user=request.user
    ).order_by('-request_date')
    
    # Status badge classes
    status_classes = {
        'PENDING': 'badge-secondary',
        'APPROVED': 'badge-success',
        'REJECTED': 'badge-danger',
        'PROCESSED': 'badge-info',
    }
    
    context = {
        'returns': returns,
        'status_classes': status_classes,
    }
    return render(request, 'orders/return_list.html', context)

@login_required
def return_detail(request, pk):
    return_request = get_object_or_404(ReturnRequest, id=pk, user=request.user)
    
    context = {
        'return': return_request,
        'status_badges': {
            'PENDING': 'badge-secondary',
            'APPROVED': 'badge-success',
            'REJECTED': 'badge-danger',
            'PROCESSED': 'badge-info',
        }
    }
    return render(request, 'orders/return_detail.html', context)


@login_required
def cancel_return(request, pk):
    """
    View to cancel a return request
    Only allows cancellation if return status is PENDING
    """
    return_request = get_object_or_404(
        ReturnRequest, 
        id=pk, 
        user=request.user,
        status='PENDING'  # Only allow cancellation for pending returns
    )
    
    if request.method == 'POST':
        return_request.status = 'CANCELLED'
        return_request.save()
        messages.success(request, f"Return request #{return_request.id} has been cancelled.")
        return redirect('return_list')
    
    
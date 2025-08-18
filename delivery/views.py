from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ShippingZone, PickupPoint
from orders.models import Order

@login_required
def delivery_dashboard(request):
    """Main delivery dashboard view"""
    pending_orders = Order.objects.filter(status='shipped').order_by('-created_at')[:10]
    recent_deliveries = Order.objects.filter(status='delivered').order_by('-delivery_date')[:5]
    
    context = {
        'pending_orders': pending_orders,
        'recent_deliveries': recent_deliveries,
        'orders_count': pending_orders.count()
    }
    return render(request, 'delivery/dashboard.html', context)

@login_required
def track_delivery(request, tracking_number):
    """Track a specific delivery"""
    order = get_object_or_404(Order, tracking_number=tracking_number)
    
    # Mock delivery status - replace with real tracking logic
    delivery_status = [
        {'status': 'Order Processed', 'date': order.created_at, 'location': 'Warehouse'},
        {'status': 'Shipped', 'date': order.estimated_delivery, 'location': 'Transit'},
        {'status': 'Out for Delivery', 'date': order.estimated_delivery, 'location': 'Local Hub'},
    ]
    
    if order.status == 'delivered':
        delivery_status.append(
            {'status': 'Delivered', 'date': order.delivery_date, 'location': order.billing_city}
        )
    
    context = {
        'order': order,
        'delivery_status': delivery_status,
        'current_status': order.get_status_display()
    }
    return render(request, 'delivery/track.html', context)

@login_required
def shipping_zones(request):
    """Display available shipping zones"""
    zones = ShippingZone.objects.filter(is_active=True).order_by('name')
    context = {
        'zones': zones
    }
    return render(request, 'delivery/zones.html', context)

@login_required
def pickup_points(request):
    """Display available pickup points"""
    points = PickupPoint.objects.filter(is_active=True).order_by('city', 'name')
    context = {
        'pickup_points': points
    }
    return render(request, 'delivery/pickup_points.html', context)
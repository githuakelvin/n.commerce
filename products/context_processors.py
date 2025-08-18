from .models import Category, Cart
from django.contrib.auth import get_user_model

User = get_user_model()

def cart(request):
    """Add cart information to the template context."""
    cart_data = {
        'cart_items_count': 0,
        'cart_total': 0,
        'cart_items': [],
    }
    
    if request.user.is_authenticated:
        # User is logged in, get their cart
        cart_obj, created = Cart.objects.get_or_create(user=request.user)
        cart_data['cart_items_count'] = cart_obj.get_total_items()
        cart_data['cart_total'] = cart_obj.get_total_price()
        cart_data['cart_items'] = cart_obj.get_cart_items()
    else:
        # User is not logged in, use session-based cart
        session_key = request.session.session_key
        if session_key:
            cart_obj, created = Cart.objects.get_or_create(session_key=session_key)
            cart_data['cart_items_count'] = cart_obj.get_total_items()
            cart_data['cart_total'] = cart_obj.get_total_price()
            cart_data['cart_items'] = cart_obj.get_cart_items()
    
    return {'cart': cart_data}


def categories(request):
    """Add categories to the template context."""
    categories_list = Category.objects.filter(is_active=True).order_by('display_order', 'name')
    return {'categories': categories_list}


def featured_products(request):
    """Add featured products to the template context."""
    from .models import Product
    featured = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).order_by('-created_at')[:8]
    return {'featured_products': featured}


def new_arrivals(request):
    """Add new arrival products to the template context."""
    from .models import Product
    new_arrivals = Product.objects.filter(
        is_active=True, 
        is_new_arrival=True
    ).order_by('-created_at')[:8]
    return {'new_arrivals': new_arrivals}


def bestsellers(request):
    """Add bestseller products to the template context."""
    from .models import Product
    bestsellers = Product.objects.filter(
        is_active=True, 
        is_bestseller=True
    ).order_by('-sold_count', '-view_count')[:8]
    return {'bestsellers': bestsellers}



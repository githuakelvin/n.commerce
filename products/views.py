from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Product, Category, Brand, Cart, CartItem, Wishlist
from .context_processors import featured_products, new_arrivals, bestsellers


def home(request):
    """Home page view."""
    context = {
        'featured_products': featured_products(request)['featured_products'],
        'new_arrivals': new_arrivals(request)['new_arrivals'],
        'bestsellers': bestsellers(request)['bestsellers'],
    }
    return render(request, 'products/home.html', context)


def category_detail(request, slug):
    """Category detail view."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category, 
        is_active=True
    ).order_by('-created_at')
    
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category_detail.html', context)


def brand_detail(request, slug):
    """Brand detail view."""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    products = Product.objects.filter(
        brand=brand, 
        is_active=True
    ).order_by('-created_at')
    
    context = {
        'brand': brand,
        'products': products,
    }
    return render(request, 'products/brand_detail.html', context)


def product_search(request):
    """Product search view."""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )
    
    if category:
        products = products.filter(category__slug=category)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    products = products.order_by(sort_by)
    
    context = {
        'products': products,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'products/search_results.html', context)


def product_detail(request, slug):
    """Product detail view."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    # Increment view count
    product.increment_view_count()
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def cart_view(request):
    """Shopping cart view."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    context = {
        'cart': cart,
    }
    return render(request, 'products/cart.html', context)


@require_POST
@csrf_exempt
def add_to_cart(request, product_id):
    """Add product to cart."""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_key=session_key)
        
        # Check if product is already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_items_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@require_POST
@csrf_exempt
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        cart = cart_item.cart
        return JsonResponse({
            'success': True,
            'message': 'Cart updated successfully',
            'cart_items_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price()),
            'subtotal': float(cart.get_total_price()),
            'total': float(cart.get_total_price())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@require_POST
@csrf_exempt
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    try:
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart = cart_item.cart
        cart_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Item removed from cart',
            'cart_items_count': cart.get_total_items(),
            'cart_total': float(cart.get_total_price())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@require_POST
@csrf_exempt
def clear_cart(request):
    """Clear entire cart."""
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            session_key = request.session.session_key
            cart = Cart.objects.get(session_key=session_key)
        
        cart.clear()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared successfully',
            'cart_items_count': 0,
            'cart_total': 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def wishlist_view(request):
    """User wishlist view."""
    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'products/wishlist.html', context)


@require_POST
@csrf_exempt
@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist."""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to wishlist'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Product already in wishlist'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@require_POST
@csrf_exempt
@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist."""
    try:
        wishlist_item = get_object_or_404(
            Wishlist, 
            user=request.user, 
            product_id=product_id
        )
        wishlist_item.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Product removed from wishlist'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


@login_required
def add_review(request, slug):
    """Add product review."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    
    if request.method == 'POST':
        # Handle review submission
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        # Create review (you'll need to implement the ProductReview model)
        # review = ProductReview.objects.create(
        #     product=product,
        #     user=request.user,
        #     rating=rating,
        #     title=title,
        #     comment=comment
        # )
        
        messages.success(request, 'Review submitted successfully!')
        return redirect('products:product_detail', slug=slug)
    
    return render(request, 'products/add_review.html', {'product': product})


# API Views
def product_list_api(request):
    """API endpoint for product listing."""
    products = Product.objects.filter(is_active=True)
    
    # Apply filters
    category = request.GET.get('category')
    if category:
        products = products.filter(category__slug=category)
    
    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand__slug=brand)
    
    # Apply search
    search = request.GET.get('q')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Apply sorting
    sort_by = request.GET.get('sort', '-created_at')
    products = products.order_by(sort_by)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    # Serialize products
    product_data = []
    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'price': float(product.price),
            'image': product.get_main_image().url if product.get_main_image() else None,
            'category': product.category.name,
            'brand': product.brand.name if product.brand else None,
            'rating': product.reviews.count(),
            'url': product.get_absolute_url()
        })
    
    return JsonResponse({
        'results': product_data,
        'count': paginator.count,
        'pages': paginator.num_pages,
        'current_page': int(page)
    })


def product_detail_api(request, slug):
    """API endpoint for product detail."""
    try:
        product = Product.objects.get(slug=slug, is_active=True)
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'description': product.description,
            'short_description': product.short_description,
            'price': float(product.price),
            'compare_price': float(product.compare_price) if product.compare_price else None,
            'stock_quantity': product.stock_quantity,
            'category': product.category.name,
            'brand': product.brand.name if product.brand else None,
            'images': [img.image.url for img in product.images.all()],
            'specifications': [
                {'name': spec.name, 'value': spec.value} 
                for spec in product.specifications.all()
            ],
            'reviews': [
                {
                    'user': review.user.username,
                    'rating': review.rating,
                    'title': review.title,
                    'comment': review.comment,
                    'created_at': review.created_at.isoformat()
                }
                for review in product.reviews.filter(is_approved=True)
            ],
            'url': product.get_absolute_url()
        }
        
        return JsonResponse(product_data)
        
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


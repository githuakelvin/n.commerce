from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Product listings
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('search/', views.product_search, name='product_search'),
    
    # Product details
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # Cart management
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Reviews
    path('product/<slug:slug>/review/', views.add_review, name='add_review'),
    
    # API endpoints
    path('api/products/', views.product_list_api, name='product_list_api'),
    path('api/products/<slug:slug>/', views.product_detail_api, name='product_detail_api'),
]





from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/shipping/', views.shipping_info, name='shipping_info'),
    path('checkout/payment/', views.payment_info, name='payment_info'),
    path('checkout/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('', views.order_list, name='order_list'),

    # Order management
    path('order/<int:pk>/', views.order_detail, name='order_detail'),
    path('order/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:pk>/track/', views.track_order, name='track_order'),
    
    # Order history
    path('history/', views.order_history, name='order_history'),
   
    
    # Returns
    path('return/<int:order_id>/', views.create_return, name='create_return'),
    path('returns/', views.return_list, name='return_list'),
    path('return/<int:pk>/detail/', views.return_detail, name='return_detail'),
    path('return/<int:pk>/cancel/', views.cancel_return, name='cancel_return'), 
]



from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment processing
    path('initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('status/<int:payment_id>/', views.payment_status, name='payment_status'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
    
    # Payment history
    path('history/', views.PaymentHistoryView.as_view(), name='payment_history'),
    path('detail/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    
    # Refunds
    path('refund/<int:payment_id>/', views.request_refund, name='request_refund'),
    path('refund/detail/<int:refund_id>/', views.refund_detail, name='refund_detail'),
    
    # Payment method specific
    path('mpesa/<int:payment_id>/', views.initiate_mpesa_payment, name='mpesa_payment'),
    path('card/<int:payment_id>/', views.initiate_card_payment, name='card_payment'),
]
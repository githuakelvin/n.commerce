from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    # Delivery tracking
    path('track/<str:tracking_number>/', views.track_delivery, name='track_delivery'),
    path('zones/', views.shipping_zones, name='shipping_zones'),
    path('pickup-points/', views.pickup_points, name='pickup_points'),
    path('dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
]


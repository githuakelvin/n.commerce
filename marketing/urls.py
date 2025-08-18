from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    
    # Promotions
    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/<str:code>/', views.coupon_detail, name='coupon_detail'),
    
    # Social media
    path('social-links/', views.social_links, name='social_links'),
]


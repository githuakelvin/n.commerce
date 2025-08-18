from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import NewsletterSubscriber, Coupon, SocialMediaLink
from .forms import NewsletterSubscriptionForm, CouponForm, SocialMediaLinkForm

def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={'is_active': True}
            )
            if created or not subscriber.is_active:
                subscriber.is_active = True
                subscriber.unsubscribed_at = None
                subscriber.save()
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')
            return redirect('home')  # Change to your desired redirect
    else:
        form = NewsletterSubscriptionForm()
    
    return render(request, 'marketing/newsletter_subscribe.html', {'form': form})

def newsletter_unsubscribe(request, token):
    subscriber = get_object_or_404(NewsletterSubscriber, token=token)
    if subscriber.is_active:
        subscriber.is_active = False
        subscriber.unsubscribed_at = timezone.now()
        subscriber.save()
        messages.success(request, 'You have been unsubscribed from our newsletter.')
    else:
        messages.info(request, 'You are already unsubscribed.')
    return redirect('home')  # Change to your desired redirect

def coupon_list(request):
    active_coupons = Coupon.objects.filter(is_active=True, valid_to__gte=timezone.now())
    return render(request, 'marketing/coupon_list.html', {'coupons': active_coupons})

def coupon_detail(request, code):
    coupon = get_object_or_404(Coupon, code=code)
    is_valid = coupon.is_valid
    return render(request, 'marketing/coupon_detail.html', {'coupon': coupon, 'is_valid': is_valid})

def social_links(request):
    links = SocialMediaLink.objects.filter(is_active=True).order_by('display_order')
    return render(request, 'marketing/social_links.html', {'links': links})
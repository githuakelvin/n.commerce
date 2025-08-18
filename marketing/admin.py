from django.contrib import admin
from .models import NewsletterSubscriber, Coupon, SocialMediaLink

admin.site.register(NewsletterSubscriber)
admin.site.register(Coupon)
admin.site.register(SocialMediaLink)
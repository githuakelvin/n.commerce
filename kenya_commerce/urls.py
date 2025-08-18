"""
URL configuration for kenya_commerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('delivery/', include('delivery.urls')),
    path('marketing/', include('marketing.urls')),
    path('blog/', include('blog.urls')),
    path('', RedirectView.as_view(url='/products/', permanent=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "Kenya Commerce Admin"
admin.site.site_title = "Kenya Commerce Admin Portal"
admin.site.index_title = "Welcome to Kenya Commerce Admin Portal"


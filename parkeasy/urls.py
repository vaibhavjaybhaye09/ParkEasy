from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('owner/', include('owner.urls')),
    path('customer/', include('customer.urls')),
    path('payment/', include('payment.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('', include('accounts.urls')),  # default home/redirects
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

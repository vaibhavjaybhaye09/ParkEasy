from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('owner/', include('owner.urls')),
    path('customer/', include('customer.urls')),
    path('payment/', include('payment.urls')),
    path('', include('accounts.urls')),  # default home/redirects
]

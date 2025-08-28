from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='payment_success'),
    path('failed/', views.failed, name='payment_failed'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:receipt_id>/', views.success, name='payment_success'),
    path('failed/', views.failed, name='payment_failed'),
    path('generate-receipt/<int:booking_id>/', views.generate_receipt, name='generate_receipt'),
    path('receipt/<int:receipt_id>/', views.view_receipt, name='view_receipt'),
    path('my-receipts/', views.my_receipts, name='my_receipts'),
]

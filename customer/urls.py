from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='customer_dashboard'),
    path('search/', views.search, name='customer_search'),
    path('place/<int:place_id>/', views.place_detail, name='customer_place_detail'),
    path('book/<int:slot_id>/', views.book, name='customer_book'),
    path('my-bookings/', views.my_bookings, name='customer_my_bookings'),
    path('profile/', views.profile_edit, name='customer_profile_edit'),
    path('settings/', views.settings_view, name='customer_settings'),
]

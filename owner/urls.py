from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='owner_dashboard'),
    path('places/add/', views.add_place, name='owner_add_place'),
    path('places/<int:place_id>/edit/', views.edit_place, name='owner_edit_place'),
    path('places/<int:place_id>/delete/', views.delete_place, name='owner_delete_place'),
    path('places/<int:place_id>/slots/', views.slots, name='owner_slots'),
    path('slots/<int:slot_id>/edit/', views.slot_edit, name='owner_slot_edit'),
    path('slots/<int:slot_id>/delete/', views.slot_delete, name='owner_slot_delete'),
    path('profile/edit/', views.profile_edit, name='owner_profile_edit'),
    path('bookings/', views.bookings, name='owner_bookings'),
    path('payments/', views.payments, name='owner_payments'),
]

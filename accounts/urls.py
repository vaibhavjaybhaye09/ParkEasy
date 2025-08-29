from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),
    path('logout/', views.custom_logout, name='custom_logout'),
    path('select-role/', views.select_role, name='select_role'),
]

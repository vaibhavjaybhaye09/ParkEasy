from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.core.exceptions import ValidationError
from functools import wraps
from django.utils import timezone
from .models import UserProfile
from .forms import SignupForm, OTPVerificationForm, ResendOTPForm, ForgotPasswordForm, PasswordResetForm, PasswordResetOTPForm
from .utils import send_otp_email, send_welcome_email, send_password_reset_email
from django import forms
import secrets
import hashlib
from datetime import datetime, timedelta


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if user is suspended
            if user.is_suspended:
                messages.error(request, f'Your account has been suspended. Reason: {user.suspension_reason}')
                return render(request, 'registration/login.html', {'form': AuthenticationForm()})
            
            if user.email_verified:
                login(request, user)
                return redirect('redirect_after_login')
            else:
                messages.error(request, 'Please verify your email before logging in.')
                return redirect('verify_otp', user_id=user.id)
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Create a simple form for error handling
    from django.contrib.auth.forms import AuthenticationForm
    form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Check if email already exists
            email = form.cleaned_data['email']
            if UserProfile.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return render(request, 'accounts/signup.html', {'form': form})
            
            # Create user but don't save yet
            user = form.save(commit=False)
            user.email = email
            user.role = form.cleaned_data['role']
            user.is_active = False  # User must verify email first
            user.save()
            
            print(f"Created user: {user.username} with email: {user.email}")
            
            # Generate and send OTP
            otp = user.generate_otp()
            print(f"Generated OTP: {otp} for user: {user.username}")
            
            if send_otp_email(email, otp, user.username):
                print(f"OTP email sent successfully to {email}")
                messages.success(request, f'Account created! Please check your email ({email}) for verification code.')
                return redirect('verify_otp', user_id=user.id)
            else:
                print(f"Failed to send OTP email to {email}")
                messages.error(request, 'Account created but failed to send verification email. Please contact support.')
                return redirect('login')
        else:
            print(f"Signup form errors: {form.errors}")
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def verify_otp(request, user_id):
    """Verify OTP and activate user account"""
    try:
        user = UserProfile.objects.get(id=user_id)
        print(f"Verifying OTP for user: {user.username} (ID: {user_id})")
        print(f"User email: {user.email}")
        print(f"User OTP: {user.otp}")
        print(f"OTP created at: {user.otp_created_at}")
        print(f"OTP expired: {user.is_otp_expired()}")
        print(f"Email verified: {user.email_verified}")
    except UserProfile.DoesNotExist:
        print(f"User with ID {user_id} not found")
        messages.error(request, 'Invalid verification link.')
        return redirect('signup')
    
    if user.email_verified:
        print(f"User {user.username} already verified")
        messages.info(request, 'Your email is already verified. Please log in.')
        return redirect('login')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            print(f"Submitted OTP: {otp}")
            print(f"Stored OTP: {user.otp}")
            print(f"OTP match: {user.otp == otp}")
            print(f"OTP expired: {user.is_otp_expired()}")
            
            if user.otp == otp and not user.is_otp_expired():
                # Verify user
                user.email_verified = True
                user.is_active = True
                user.otp = None
                user.otp_created_at = None
                user.save()
                print(f"User {user.username} verified successfully")
                
                # Send welcome email
                send_welcome_email(user.email, user.username)
                
                messages.success(request, 'Email verified successfully! You can now log in.')
                return redirect('login')
            elif user.is_otp_expired():
                print(f"OTP expired for user {user.username}")
                messages.error(request, 'OTP has expired. Please request a new one.')
            else:
                print(f"Invalid OTP for user {user.username}")
                messages.error(request, 'Invalid OTP. Please check and try again.')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = OTPVerificationForm()
    
    return render(request, 'accounts/verify_otp.html', {
        'form': form, 
        'user': user,
        'email': user.email
    })


def resend_otp(request):
    """Resend OTP to user's email"""
    if request.method == 'POST':
        form = ResendOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = UserProfile.objects.get(email=email)
                if user.email_verified:
                    messages.info(request, 'Your email is already verified. Please log in.')
                    return redirect('login')
                
                # Generate new OTP
                otp = user.generate_otp()
                if send_otp_email(email, otp, user.username):
                    messages.success(request, f'New verification code sent to {email}')
                    return redirect('verify_otp', user_id=user.id)
                else:
                    messages.error(request, 'Failed to send verification email. Please try again.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = ResendOTPForm()
    
    return render(request, 'accounts/resend_otp.html', {'form': form})


def forgot_password(request):
    """Handle forgot password request - send reset link"""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            print(f"Password reset requested for email: {email}")
            
            try:
                user = UserProfile.objects.get(email=email)
                print(f"User found: {user.username}")
                print(f"Email verified: {user.email_verified}")
                
                if not user.email_verified:
                    print(f"User {user.username} email not verified")
                    messages.error(request, 'Please verify your email first before resetting password. Check your email for verification link.')
                    return render(request, 'accounts/forgot_password.html', {'form': form})
                
                # Check if user is suspended
                if user.is_suspended:
                    print(f"User {user.username} is suspended")
                    messages.error(request, f'Your account has been suspended. Reason: {user.suspension_reason}')
                    return render(request, 'accounts/forgot_password.html', {'form': form})
                
                # Generate reset token
                token = secrets.token_urlsafe(32)
                print(f"Generated reset token: {token}")
                
                user.password_reset_token = token
                user.password_reset_expires = timezone.now() + timedelta(hours=24)  # 24 hours expiry
                user.save()
                print(f"Reset token saved for user {user.username}")
                
                # Create reset link
                reset_link = request.build_absolute_uri(f'/accounts/reset-password/{token}/')
                print(f"Reset link: {reset_link}")
                
                if send_password_reset_email(email, reset_link, user.username):
                    print(f"Password reset email sent successfully to {email}")
                    messages.success(request, f'Password reset link sent to {email}. Please check your email and spam folder.')
                else:
                    print(f"Failed to send password reset email to {email}")
                    messages.error(request, 'Failed to send reset email. Please try again later or contact support.')
            except UserProfile.DoesNotExist:
                print(f"No user found with email: {email}")
                messages.error(request, 'No account found with this email address. Please check the email address or create a new account.')
            except Exception as e:
                print(f"Error in forgot password: {e}")
                messages.error(request, 'An error occurred. Please try again later.')
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})


def verify_password_reset_otp(request, user_id):
    """Verify OTP for password reset"""
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid user.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = PasswordResetOTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            if user.otp == otp and not user.is_otp_expired():
                # OTP is valid, redirect to password reset form
                return redirect('reset_password_with_otp', user_id=user.id)
            elif user.is_otp_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
            else:
                messages.error(request, 'Invalid OTP. Please check and try again.')
    else:
        form = PasswordResetOTPForm()
    
    return render(request, 'accounts/verify_password_reset_otp.html', {
        'form': form, 
        'user': user,
        'email': user.email
    })


def reset_password_with_otp(request, user_id):
    """Reset password after OTP verification"""
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid user.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Update password
            user.set_password(form.cleaned_data['password1'])
            user.otp = None
            user.otp_created_at = None
            user.save()
            
            messages.success(request, 'Password reset successfully! You can now log in with your new password.')
            return redirect('login')
    else:
        form = PasswordResetForm()
    
    return render(request, 'accounts/reset_password_with_otp.html', {'form': form})


def reset_password(request, token):
    """Reset password using token"""
    print(f"Password reset attempt with token: {token}")
    
    try:
        # Find user with this reset token
        user = UserProfile.objects.get(password_reset_token=token)
        print(f"User found: {user.username}")
        print(f"Token expires at: {user.password_reset_expires}")
        
        # Check if token has expired
        if user.password_reset_expires and timezone.now() > user.password_reset_expires:
            print(f"Token expired for user {user.username}")
            messages.error(request, 'Password reset link has expired. Please request a new one.')
            return redirect('forgot_password')
        
        print(f"Token is valid for user {user.username}")
        
    except UserProfile.DoesNotExist:
        print(f"No user found with token: {token}")
        messages.error(request, 'Invalid password reset link.')
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            print(f"Password reset form valid for user {user.username}")
            
            # Update password
            user.set_password(form.cleaned_data['password1'])
            # Clear reset token
            user.password_reset_token = None
            user.password_reset_expires = None
            user.save()
            
            print(f"Password reset successful for user {user.username}")
            messages.success(request, 'Password reset successfully! You can now log in with your new password.')
            return redirect('login')
        else:
            print(f"Password reset form errors: {form.errors}")
    else:
        form = PasswordResetForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})


@login_required
def redirect_after_login(request):
    # If user picked a role on login, honor it and persist
    selected = request.GET.get('selected_role')
    if selected in dict(UserProfile.ROLE_CHOICES):
        request.user.role = selected
        request.user.save(update_fields=['role'])
        role = selected
    else:
        try:
            role = request.user.role
        except Exception:
            return redirect('select_role')

    if role == UserProfile.ROLE_CUSTOMER:
        return redirect('customer_dashboard')
    if role == UserProfile.ROLE_OWNER:
        return redirect('owner_dashboard')
    if role == UserProfile.ROLE_ADMIN:
        return redirect('admin_panel:dashboard')
    return redirect('/')


def home(request):
    return render(request, 'accounts/home.html')


def custom_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('/')


class SelectRoleForm(forms.Form):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,
        label='Select your role'
    )


@login_required
def select_role(request):
    try:
        profile = request.user
    except Exception:
        profile = request.user
    if request.method == 'POST':
        form = SelectRoleForm(request.POST)
        if form.is_valid():
            profile.role = form.cleaned_data['role']
            profile.save(update_fields=['role'])
            return redirect('redirect_after_login')
    else:
        form = SelectRoleForm(initial={'role': getattr(profile, 'role', UserProfile.ROLE_CUSTOMER)})
    return render(request, 'accounts/select_role.html', {'form': form})

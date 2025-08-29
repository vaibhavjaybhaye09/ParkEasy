from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.core.exceptions import ValidationError
from functools import wraps
from .models import UserProfile
from .forms import SignupForm, OTPVerificationForm, ResendOTPForm
from .utils import send_otp_email, send_welcome_email
from django import forms


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
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
            
            # Generate and send OTP
            otp = user.generate_otp()
            if send_otp_email(email, otp, user.username):
                messages.success(request, f'Account created! Please check your email ({email}) for verification code.')
                return redirect('verify_otp', user_id=user.id)
            else:
                messages.error(request, 'Account created but failed to send verification email. Please contact support.')
                return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def verify_otp(request, user_id):
    """Verify OTP and activate user account"""
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('signup')
    
    if user.email_verified:
        messages.info(request, 'Your email is already verified. Please log in.')
        return redirect('login')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            if user.otp == otp and not user.is_otp_expired():
                # Verify user
                user.email_verified = True
                user.is_active = True
                user.otp = None
                user.otp_created_at = None
                user.save()
                
                # Send welcome email
                send_welcome_email(user.email, user.username)
                
                messages.success(request, 'Email verified successfully! You can now log in.')
                return redirect('login')
            elif user.is_otp_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
            else:
                messages.error(request, 'Invalid OTP. Please check and try again.')
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

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from functools import wraps
from .models import UserProfile
from .forms import SignupForm
from django import forms


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('redirect_after_login')
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
            user = form.save()
            # persist email
            user.email = form.cleaned_data['email']
            user.save(update_fields=['email'])
            # save role to profile
            user.role = form.cleaned_data['role']
            user.save(update_fields=['role'])
            messages.success(request, 'Account created. Please log in.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


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

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.RadioSelect,
        label='Select your role'
    )

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Simplify password help text
        self.fields['password1'].help_text = 'Create a password (minimum 8 characters)'
        self.fields['password2'].help_text = 'Enter the same password again'
        
        # Make password fields more user-friendly
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Create your password',
            'minlength': '8'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm your password',
            'minlength': '8'
        })


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'phone', 'address')


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': 'Enter 6-digit OTP',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;'
        }),
        help_text='Enter the 6-digit code sent to your email'
    )


class ResendOTPForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email address'
        }),
        help_text='Enter the email address associated with your account'
    )


class PasswordResetOTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': 'Enter 6-digit OTP',
            'style': 'font-size: 1.5rem; letter-spacing: 0.5rem;'
        }),
        help_text='Enter the 6-digit code sent to your email'
    )


class PasswordResetForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter new password',
            'minlength': '8'
        }),
        help_text='Create a new password (minimum 8 characters)'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm new password',
            'minlength': '8'
        }),
        help_text='Enter the same password again'
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match")
            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long")
        
        return cleaned_data
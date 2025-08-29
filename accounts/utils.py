from functools import wraps
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def role_required(allowed_roles):
    if isinstance(allowed_roles, str):
        allowed = {allowed_roles}
    else:
        allowed = set(allowed_roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                role = request.user.role
            except Exception:
                return redirect('login')
            if role not in allowed:
                return render(request, 'accounts/forbidden.html', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def send_otp_email(user_email, otp, username):
    """
    Send OTP verification email to user
    """
    subject = 'Verify Your Email - ParkEasy'
    
    # HTML Email template
    html_message = render_to_string('accounts/email/otp_email.html', {
        'username': username,
        'otp': otp,
        'site_name': 'ParkEasy'
    })
    
    # Plain text version
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_welcome_email(user_email, username):
    """
    Send welcome email after successful verification
    """
    subject = 'Welcome to ParkEasy!'
    
    html_message = render_to_string('accounts/email/welcome_email.html', {
        'username': username,
        'site_name': 'ParkEasy',
        'site_url': 'http://localhost:8000'  # Update this with your actual domain in production
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_password_reset_email(user_email, reset_link, username):
    """
    Send password reset email
    """
    subject = 'Reset Your Password - ParkEasy'
    
    html_message = render_to_string('accounts/email/password_reset.html', {
        'username': username,
        'reset_link': reset_link,
        'site_name': 'ParkEasy'
    })
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False

# ParkEasy OTP Verification Setup Guide

## Overview
ParkEasy now includes secure OTP (One-Time Password) verification for user registration. This ensures that only users with valid email addresses can create accounts. **The system uses email verification only - no phone number required.**

## Features Added

### 1. OTP Verification System
- **6-digit OTP codes** sent via email
- **15-minute expiration** for security
- **Email verification required** before login
- **Resend OTP functionality** for convenience
- **Email-only verification** - no phone number needed

### 2. Enhanced User Model
- `email_verified` - Boolean field for verification status
- `otp` - 6-digit verification code
- `otp_created_at` - Timestamp for OTP expiration
- `phone` - Optional field (not required for registration)

### 3. Email Templates
- **OTP Email** - Professional verification email with clear instructions
- **Welcome Email** - Confirmation after successful verification
- **Responsive design** for all devices

## Setup Instructions

### Step 1: Configure Email Settings

#### Option A: Use email_config.py (Recommended)
1. Open `email_config.py`
2. Choose your email provider (GMAIL, OUTLOOK, or YAHOO)
3. Update the credentials:
   ```python
   'GMAIL': {
       'EMAIL_HOST_USER': 'your-email@gmail.com',
       'EMAIL_HOST_PASSWORD': 'your-app-password',
   }
 EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
 EMAIL_HOST = 'easypark655@gmail.com'
 EMAIL_PORT = '587'
 EMAIL_HOST_USER = 'ParkEasy'
 EMAIL_HOST_PASSWORD = 'zjxy bjmp utoy ncer'
 EMAIL_USE_TLS = 'TRUE'

#### Option B: Update settings.py directly
1. Open `ParkEasy/settings.py`
2. Update the email configuration:
   ```python
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   ```

### Step 2: Gmail App Password Setup (Recommended)

1. **Enable 2-Factor Authentication**
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Enable "2-Step Verification"

2. **Generate App Password**
   - Go to "App passwords" under 2-Step Verification
   - Select "Mail" and "Other (Custom name)"
   - Enter "ParkEasy" as the name
   - Copy the 16-character password

3. **Update Configuration**
   - Use this app password in `EMAIL_HOST_PASSWORD`
   - Never use your regular Gmail password

### Step 3: Test the System

1. **Start the server**
   ```bash
   python manage.py runserver
   ```

2. **Create a test account**
   - Go to `/accounts/signup/`
   - Fill out the form with a valid email
   - Check your email for the OTP

3. **Verify the account**
   - Enter the 6-digit OTP
   - Account should be activated

## User Flow

### New User Registration
1. User fills signup form (username, email, password, role)
2. System creates inactive user account
3. OTP is generated and sent via email
4. User receives email with 6-digit code and clear instructions
5. User enters OTP on verification page
6. Account is activated and welcome email sent
7. User can now login

### Login Process
1. User enters credentials
2. System checks if email is verified
3. If verified: Login successful
4. If not verified: Redirect to OTP verification

### OTP Expiration
- OTP codes expire after 15 minutes
- Users can request new codes via "Resend OTP"
- Old OTPs are automatically invalidated
- All verification happens via email only

## Security Features

- **Time-limited OTPs** (15 minutes)
- **One-time use** codes
- **Email verification required** for login
- **Email-only verification** - no phone dependency
- **CSRF protection** on all forms
- **Rate limiting** on OTP generation

## Email Templates

### OTP Email (`otp_email.html`)
- Professional design with ParkEasy branding
- Clear 6-digit code display
- Security warnings and expiration info
- Mobile-responsive layout

### Welcome Email (`welcome_email.html`)
- Congratulatory message after verification
- Feature highlights and next steps
- Call-to-action buttons
- Professional footer

## Troubleshooting

### Common Issues

1. **"Failed to send verification email"**
   - Check email credentials in settings
   - Verify SMTP settings are correct
   - Check if email provider allows SMTP access

2. **"OTP has expired"**
   - User waited too long to enter code
   - Use "Resend OTP" to get new code
   - Codes expire after 15 minutes

3. **"Invalid OTP"**
   - Check if code was entered correctly
   - Ensure no extra spaces
   - Verify code hasn't been used already

4. **Gmail "Less secure app access" error**
   - Use App Passwords instead of regular password
   - Enable 2-Factor Authentication first
   - Generate app-specific password

### Email Provider Settings

#### Gmail
- **SMTP Server**: smtp.gmail.com
- **Port**: 587
- **Security**: TLS
- **Authentication**: App Password required

#### Outlook/Hotmail
- **SMTP Server**: smtp-mail.outlook.com
- **Port**: 587
- **Security**: TLS
- **Authentication**: Regular password (enable less secure apps)

#### Yahoo
- **SMTP Server**: smtp.mail.yahoo.com
- **Port**: 587
- **Security**: TLS
- **Authentication**: App Password required

## Files Modified/Created

### Models
- `accounts/models.py` - Added OTP fields

### Views
- `accounts/views.py` - OTP verification logic

### Forms
- `accounts/forms.py` - OTP verification forms (removed phone requirement)

### Templates
- `accounts/verify_otp.html` - OTP verification page (email-focused)
- `accounts/resend_otp.html` - Resend OTP page (email-focused)
- `accounts/signup.html` - Removed phone field, email verification only
- `accounts/email/otp_email.html` - OTP email template with clear instructions
- `accounts/email/welcome_email.html` - Welcome email template

### URLs
- `accounts/urls.py` - New OTP routes

### Utilities
- `accounts/utils.py` - Email sending functions

### Configuration
- `ParkEasy/settings.py` - Email settings
- `email_config.py` - Email provider configurations

## Testing

### Manual Testing
1. Create new account with valid email
2. Check email for OTP
3. Verify account with OTP
4. Try logging in
5. Test OTP expiration
6. Test resend functionality

### Automated Testing
```bash
python manage.py test accounts
```

## Production Considerations

1. **Environment Variables**
   - Store email credentials in environment variables
   - Never commit passwords to version control

2. **Email Service**
   - Consider using professional email services (SendGrid, Mailgun)
   - Monitor email delivery rates

3. **Rate Limiting**
   - Implement rate limiting on OTP generation
   - Prevent abuse of resend functionality

4. **Logging**
   - Log OTP generation and verification attempts
   - Monitor for suspicious activity

## Support

If you encounter issues:
1. Check the Django console for error messages
2. Verify email configuration settings
3. Test with a simple email first
4. Check email provider's SMTP requirements

## Updates

This OTP system can be extended with:
- SMS verification (additional cost)
- Voice call verification
- Backup email addresses
- Account recovery options
- Two-factor authentication for existing users

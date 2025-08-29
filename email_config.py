# Email Configuration for ParkEasy
# Update these settings with your email provider details

# Gmail Configuration (Recommended)
EMAIL_CONFIG = {
    'GMAIL': {
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': 587,
        'EMAIL_USE_TLS': True,
        'EMAIL_USE_SSL': False,
        'EMAIL_HOST_USER': 'your-email@gmail.com',  # Replace with your Gmail
        'EMAIL_HOST_PASSWORD': 'your-app-password',  # Replace with your Gmail app password
    },
    
    'OUTLOOK': {
        'EMAIL_HOST': 'smtp-mail.outlook.com',
        'EMAIL_PORT': 587,
        'EMAIL_USE_TLS': True,
        'EMAIL_USE_SSL': False,
        'EMAIL_HOST_USER': 'your-email@outlook.com',  # Replace with your Outlook
        'EMAIL_HOST_PASSWORD': 'your-password',  # Replace with your password
    },
    
    'YAHOO': {
        'EMAIL_HOST': 'smtp.mail.yahoo.com',
        'EMAIL_PORT': 587,
        'EMAIL_USE_TLS': True,
        'EMAIL_USE_SSL': False,
        'EMAIL_HOST_USER': 'your-email@yahoo.com',  # Replace with your Yahoo
        'EMAIL_HOST_PASSWORD': 'your-app-password',  # Replace with your app password
    }
}

# Choose your email provider (GMAIL, OUTLOOK, or YAHOO)
SELECTED_PROVIDER = 'GMAIL'

# Get the selected configuration
def get_email_config():
    """Get the selected email configuration"""
    if SELECTED_PROVIDER in EMAIL_CONFIG:
        return EMAIL_CONFIG[SELECTED_PROVIDER]
    else:
        # Default to Gmail if invalid selection
        return EMAIL_CONFIG['GMAIL']

# Instructions for Gmail App Password:
"""
To use Gmail with ParkEasy:

1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
   - Use this 16-character password in EMAIL_HOST_PASSWORD

3. Update the GMAIL configuration above with your email and app password

4. Update settings.py to import from this file:
   from email_config import get_email_config
   email_config = get_email_config()
   
   EMAIL_HOST = email_config['EMAIL_HOST']
   EMAIL_PORT = email_config['EMAIL_PORT']
   EMAIL_USE_TLS = email_config['EMAIL_USE_TLS']
   EMAIL_USE_SSL = email_config['EMAIL_USE_SSL']
   EMAIL_HOST_USER = email_config['EMAIL_HOST_USER']
   EMAIL_HOST_PASSWORD = email_config['EMAIL_HOST_PASSWORD']
"""

# Instructions for other providers:
"""
For Outlook/Hotmail:
- Use your regular email password
- Make sure "Less secure app access" is enabled

For Yahoo:
- Generate an app password similar to Gmail
- Enable 2FA first, then generate app password
"""

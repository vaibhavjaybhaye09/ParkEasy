"""WSGI config for parkeasy project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkeasy.settings')
application = get_wsgi_application()

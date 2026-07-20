"""WSGI config for the VoterInfo project."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voterinfo.settings')
application = get_wsgi_application()

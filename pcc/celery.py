import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pcc.settings')

app = Celery('pcc')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# namespace='CELERY' means all celery-related config keys in settings.py must start with 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically load task modules from all registered Django apps.
app.autodiscover_tasks()
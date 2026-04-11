"""
Development settings for pcc project.

Use for local development only. Do NOT use in production.
"""

from .base import *  # noqa: F401, F403

# Development overrides - allow DEBUG to default True via .env
# but ensure ALLOWED_HOSTS has useful defaults for local dev
if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# In development, session and CSRF cookies do not require HTTPS
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True

# No HTTPS redirect in development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

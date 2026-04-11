"""
Production settings for pcc project.

Strict security settings. Requires all environment variables to be set.
"""

from .base import *  # noqa: F401, F403

# Production must have DEBUG=False
DEBUG = False  # noqa: F405

# HTTPS / SSL security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session cookie security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# CSRF cookie security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# HTTP Strict Transport Security (HSTS) - 1 year
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content security
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

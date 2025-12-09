"""
Production specific settings.
"""
from .base import *

# Debug settings
DEBUG = False

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - MongoDB for production
DATABASES['default'] = {
    'ENGINE': 'djongo',
    'NAME': config('DB_NAME', default='company_services'),
    'CLIENT': {
        'host': config('DB_HOST', default='localhost'),
        'port': config('DB_PORT', default=27017, cast=int),
        'username': config('DB_USER', default=''),
        'password': config('DB_PASSWORD', default=''),
        'authSource': config('DB_AUTH_SOURCE', default='admin'),
        'authMechanism': config('DB_AUTH_MECHANISM', default='SCRAM-SHA-256'),
    },
    'CONN_MAX_AGE': 600,
}

# Redis cache for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        }
    }
}

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@company-services.nl')

# CORS settings for production
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())
CORS_ALLOW_ALL_ORIGINS = False

# Static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging configuration for production
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['handlers']['mail_admins']['level'] = 'ERROR'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['company_services']['level'] = 'INFO'

# Add Sentry for error tracking (optional)
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

# sentry_sdk.init(
#     dsn=config('SENTRY_DSN', default=''),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=1.0,
#     send_default_pii=True
# )

# Admin URL for security
ADMIN_URL = config('ADMIN_URL', default='admin/')
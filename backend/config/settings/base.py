"""
Django settings for company_services project.
"""

import os
import sys
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add apps directory to Python path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'drf_yasg',  # API documentation
    'import_export',
    'whitenoise.runserver_nostatic',  # For static files

    'products',

    
    
    # Local apps
    'core.apps.CoreConfig',
    'core.templatetags.custom_tags',
    'core.templatetags.custom_i18n',
    'authentication.apps.AuthenticationConfig',
    'clients.apps.ClientsConfig',
    'contact.apps.ContactConfig',
    'quotes.apps.QuotesConfig',
    'services.apps.ServicesConfig',
    'projects.apps.ProjectsConfig',
    'vehicles.apps.VehiclesConfig',
    'analytics.apps.AnalyticsConfig',
    'notifications.apps.NotificationsConfig',
    'orders.apps.OrdersConfig',
]

# Custom user model - FIXED: Use authentication.CustomUser
AUTH_USER_MODEL = 'authentication.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # For i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom middleware (optional - create these later)
    # 'core.middleware.RequestLoggingMiddleware',
    # 'core.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'core.context_processors.site_config',  # Custom context processor
                'core.context_processors.current_year',  # Custom context processor
            ],
            'libraries': {
                # 'custom_tags': 'core.templatetags.custom_tags',  # Custom template tags,
                
            },
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# For development - using SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20, # Increase timeout for database locks is 20 seconds
        }
    }
}
# python manage.py collectstatic is to be used to collect static files for production

# For production - MongoDB with Djongo (uncomment when ready)
# DATABASES = {
#     'default': {
#         'ENGINE': 'djongo',
#         'NAME': config('DB_NAME', default='company_services'),
#         'CLIENT': {
#             'host': config('DB_HOST', default='localhost'),
#             'port': config('DB_PORT', default=27017, cast=int),
#             'username': config('DB_USER', default=''),
#             'password': config('DB_PASSWORD', default=''),
#             'authSource': config('DB_AUTH_SOURCE', default='admin'),
#             'authMechanism': config('DB_AUTH_MECHANISM', default='SCRAM-SHA-256'),
#         },
#         'CONN_MAX_AGE': config('DB_CONN_MAX_AGE', default=600, cast=int),
#     }
# }

# Optional PostgreSQL for analytics/reporting
# DATABASES['postgres'] = {
#     'ENGINE': 'django.db.backends.postgresql',
#     'NAME': config('PG_DB_NAME', default='company_services_analytics'),
#     'USER': config('PG_DB_USER', default='postgres'),
#     'PASSWORD': config('PG_DB_PASSWORD', default=''),
#     'HOST': config('PG_DB_HOST', default='localhost'),
#     'PORT': config('PG_DB_PORT', default=5432, cast=int),
# }

# Database router for multiple databases
# DATABASE_ROUTERS = ['core.db_routers.PrimaryReplicaRouter']

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('email', 'first_name', 'last_name'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'nl-nl'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_TZ = True

# Locale paths
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Languages
LANGUAGES = [
    ('nl', 'Nederlands'),
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('ar', 'العربية'),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Admin site customization
ADMIN_SITE_HEADER = "Company Services Admin"
ADMIN_SITE_TITLE = "Company Services Administration"
ADMIN_INDEX_TITLE = "Welcome to Company Services Admin"

# Email configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='webmaster@localhost')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')

# CORS settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000',
    cast=Csv()
)

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# For production Redis cache
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'PASSWORD': config('REDIS_PASSWORD', default=''),
#         }
#     }
# }

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=False, cast=bool)
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF configuration
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=False, cast=bool)
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings (for production)
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'company_services': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
log_dir = BASE_DIR / 'logs'
log_dir.mkdir(exist_ok=True)

# Django Extensions (for development)
GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}

# API Documentation (drf-yasg)
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': True,
    'JSON_EDITOR': True,
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': True,
    'PERSIST_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'REFETCH_SCHEMA_ON_LOGOUT': True,
}

# Application specific settings
CONTACT_SETTINGS = {
    'MAX_ATTACHMENTS_PER_MESSAGE': 5,
    'MAX_ATTACHMENT_SIZE': 10 * 1024 * 1024,  # 10MB
    'REQUIRE_CAPTCHA': False,
    'DEFAULT_FROM_EMAIL': 'noreply@company-services.nl',
    'ADMIN_EMAIL': 'admin@company-services.nl',
    'SITE_URL': config('SITE_URL', default='http://localhost:8000'),
    'SITE_NAME': 'Company Services',
    'CAPTCHA_SECRET_KEY': config('CAPTCHA_SECRET_KEY', default=''),
    'CAPTCHA_SITE_KEY': config('CAPTCHA_SITE_KEY', default=''),
}

QUOTE_SETTINGS = {
    'DEFAULT_VALIDITY_DAYS': 30,
    'DEFAULT_CURRENCY': 'EUR',
    'DEFAULT_TAX_RATE': 21.00,
    'QUOTE_NUMBER_PREFIX': 'QT',
    'PDF_TEMPLATE': 'quotes/templates/quote_pdf.html',
    'ALLOWED_ATTACHMENT_TYPES': [
        'application/pdf',
        'image/jpeg', 'image/png', 'image/gif',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ],
    'MAX_ATTACHMENT_SIZE': 10 * 1024 * 1024,  # 10MB
    'AUTO_EXPIRE_DAYS': 30,
    'FOLLOWUP_DAYS': 7,
}

PRODUCT_SETTINGS = {
    'DEFAULT_CURRENCY': 'EUR',
    'DEFAULT_TAX_RATE': 21.00,
    'LOW_STOCK_THRESHOLD': 10,
    'IMAGE_MAX_SIZE': 5 * 1024 * 1024,  # 5MB
    'ALLOWED_IMAGE_TYPES': ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    'FEATURED_PRODUCTS_LIMIT': 10,
    'RELATED_PRODUCTS_LIMIT': 5,
}

SERVICE_SETTINGS = {
    'DEFAULT_CURRENCY': 'EUR',
    'DEFAULT_TAX_RATE': 21.00,
    'IMAGE_MAX_SIZE': 5 * 1024 * 1024,  # 5MB
    'ALLOWED_IMAGE_TYPES': ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
    'EMERGENCY_RESPONSE_HOURS': 24,
    'STANDARD_RESPONSE_HOURS': 72,
}

# File validation settings
FILE_VALIDATION = {
    'ALLOWED_IMAGE_TYPES': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    'ALLOWED_DOCUMENT_TYPES': [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain',
        'text/csv',
    ],
    'MAX_IMAGE_SIZE': 5 * 1024 * 1024,  # 5MB
    'MAX_DOCUMENT_SIZE': 10 * 1024 * 1024,  # 10MB
    'MAX_VIDEO_SIZE': 50 * 1024 * 1024,  # 50MB
}

# Site configuration
SITE_CONFIG = {
    'COMPANY_NAME': 'Company Services BV',
    'COMPANY_EMAIL': 'info@company-services.nl',
    'COMPANY_PHONE': '+31 20 123 4567',
    'COMPANY_ADDRESS': 'Bedrijfsstraat 123, 1234 AB Amsterdam',
    'SUPPORT_EMAIL': 'support@company-services.nl',
    'SALES_EMAIL': 'sales@company-services.nl',
    'INFO_EMAIL': 'info@company-services.nl',
    'VAT_NUMBER': 'NL123456789B01',
    'KVK_NUMBER': '12345678',
    'IBAN': 'NL91 ABNA 0417 1643 00',
    'BIC': 'ABNANL2A',
}


ORDER_SETTINGS = {
    'DEFAULT_CURRENCY': 'EUR',
    'DEFAULT_TAX_RATE': 21.00,
    'ORDER_NUMBER_PREFIX': 'ORD',
    'DEFAULT_PAYMENT_TERMS': '30 dagen',
    'LATE_PAYMENT_FEE_PERCENTAGE': 5.00,
    'AUTO_CANCEL_DAYS': 30,
    'RETURN_PERIOD_DAYS': 14,
    'LOW_STOCK_ALERT_LEVEL': 10,
    'REORDER_QUANTITY': 50,
    'SHIPPING_COSTS': {
        'STANDARD': 5.95,
        'EXPRESS': 12.95,
        'FREE_THRESHOLD': 50.00,
    },
    'ALLOWED_ATTACHMENT_TYPES': [
        'application/pdf',
        'image/jpeg', 'image/png', 'image/gif',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ],
    'MAX_ATTACHMENT_SIZE': 10 * 1024 * 1024,  # 10MB
}

# Django Import Export
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = False
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'import_export.tmp_storages.CacheStorage'
IMPORT_EXPORT_IMPORT_PERMISSION_CODE = 'change'
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'view'

# Django Cleanup (auto delete orphaned files)
CLEANUP_KEEP_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx']
CLEANUP_KEEP_NEW_FILES_FOR_DAYS = 1

# Test settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_OUTPUT_DIR = BASE_DIR / 'test_reports'

# Performance settings
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000  # Higher limit for complex forms

# Django Debug Toolbar (development only)
if DEBUG:

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]
    
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'RESULTS_CACHE_SIZE': 100,
        'SHOW_COLLAPSED': True,
        'SQL_WARNING_THRESHOLD': 100,  # milliseconds
    }
    
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
"""
Django settings for External Connectivity Microservice.

This configuration uses environment variables for all sensitive data
and deployment-specific settings, following cloud-native best practices.
"""

import os
from pathlib import Path
from datetime import timedelta
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production-please')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', 'web', '*'])

# Application environment (development, staging, production)
APP_ENV = env('APP_ENV', default='development')

# ==============================================================================
# APPLICATION DEFINITION
# ==============================================================================

INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_prometheus',
    'drf_spectacular',
    'health_check',
    'health_check.db',
    'health_check.cache',
    
    # Local apps (3 core functions)
    'apps.citizen_validation',      # Function #1: Validate citizen existence
    'apps.citizen_registration',    # Function #2: Register citizen in centralizer
    'apps.document_authentication', # Function #3: Authenticate documents
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'

# ==============================================================================
# DATABASE CONFIGURATION (MariaDB/MySQL)
# ==============================================================================

# Use DATABASE_URL for simplified database configuration
# Format: mysql://user:password@host:port/database
DATABASES = {'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')}

# ==============================================================================
# CACHE CONFIGURATION
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'connectivity-cache',
    }
}

# ==============================================================================
# AUTHENTICATION & SECURITY
# ==============================================================================

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
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

# Security settings
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ==============================================================================
# REST FRAMEWORK CONFIGURATION
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env('THROTTLE_ANON', default='100/hour'),
        'user': env('THROTTLE_USER', default='1000/hour'),
    }
}

# ==============================================================================
# OAUTH2 CLIENT CREDENTIALS CONFIGURATION
# ==============================================================================
# JWT validation for OAuth2 Client Credentials from auth-microservice
AUTH_SERVICE_JWT_SECRET = env('AUTH_SERVICE_JWT_SECRET', default='shared-secret-with-auth-service')
AUTH_SERVICE_JWT_ALGORITHM = env('AUTH_SERVICE_JWT_ALGORITHM', default='HS256')

# ==============================================================================
# CORS CONFIGURATION
# ==============================================================================

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
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

# ==============================================================================
# RABBITMQ CONFIGURATION
# ==============================================================================

RABBITMQ_HOST = env('RABBITMQ_HOST', default='localhost')
RABBITMQ_PORT = env.int('RABBITMQ_PORT', default=5672)
RABBITMQ_USER = env('RABBITMQ_USER', default='guest')
RABBITMQ_PASSWORD = env('RABBITMQ_PASSWORD', default='guest')
RABBITMQ_VHOST = env('RABBITMQ_VHOST', default='/')
RABBITMQ_EXCHANGE = env('RABBITMQ_EXCHANGE', default='connectivity')

# RabbitMQ Queue Names and Routing Keys
RABBITMQ_DOCUMENT_AUTH_QUEUE = env('RABBITMQ_DOCUMENT_AUTH_QUEUE', default='document.authentication.requested')
RABBITMQ_DOCUMENT_AUTH_ROUTING_KEY = env('RABBITMQ_DOCUMENT_AUTH_ROUTING_KEY', default='document.authentication.requested')
RABBITMQ_AUTH_USER_REGISTERED_QUEUE = env('RABBITMQ_AUTH_USER_REGISTERED_QUEUE', default='auth.user.registered')
RABBITMQ_AUTH_USER_REGISTERED_ROUTING_KEY = env('RABBITMQ_AUTH_USER_REGISTERED_ROUTING_KEY', default='auth.user.registered')

# ==============================================================================
# EXTERNAL API CONFIGURATION
# ==============================================================================

EXTERNAL_GOVCARPETA_API_URL = env('EXTERNAL_GOVCARPETA_API_URL', default='https://govcarpeta-apis-4905ff3c005b.herokuapp.com')
EXTERNAL_GOVCARPETA_API_KEY = env('EXTERNAL_GOVCARPETA_API_KEY', default='')
EXTERNAL_API_TIMEOUT = env.int('EXTERNAL_API_TIMEOUT', default=30)

# Operator configuration for citizen registration
EXTERNAL_GOVCARPETA_OPERATOR_ID = env('EXTERNAL_GOVCARPETA_OPERATOR_ID', default='65ca0a00d833e984e26087569')
EXTERNAL_GOVCARPETA_OPERATOR_NAME = env('EXTERNAL_GOVCARPETA_OPERATOR_NAME', default='Operador Ciudadano CCP')

# ==============================================================================
# AUTH MICROSERVICE INTEGRATION (OAuth2 Client Credentials)
# ==============================================================================

# JWT secret key shared with auth-microservice for token validation
# IMPORTANT: This MUST be the same secret used by auth-microservice to sign tokens
AUTH_SERVICE_JWT_SECRET = env('AUTH_SERVICE_JWT_SECRET', default=SECRET_KEY)
AUTH_SERVICE_JWT_ALGORITHM = env('AUTH_SERVICE_JWT_ALGORITHM', default='HS256')

# ==============================================================================
# API DOCUMENTATION (DRF-Spectacular)
# ==============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'External Connectivity Microservice API',
    'DESCRIPTION': 'Proxy microservice for external centralizer integration: citizen validation, registration, and document authentication',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1',
}

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

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
            'format': '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "module": "%(module)s"}',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': env('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = env('TIME_ZONE', default='UTC')
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC FILES
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

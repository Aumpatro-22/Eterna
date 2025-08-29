import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url  # NEW

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-key-for-dev')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Allow Render's external hostname if provided by platform
RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')  # NEW
if RENDER_HOSTNAME and RENDER_HOSTNAME not in ALLOWED_HOSTS:  # NEW
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)  # NEW

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Local apps
    'memorials',
    'users',
    'communities',
    'tales',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # NEW: serve static files on Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'eternal_memories.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'eternal_memories.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Override with DATABASE_URL when present (Render)
if os.environ.get('DATABASE_URL'):  # NEW
    DATABASES['default'] = dj_database_url.config(  # NEW
        default=os.environ['DATABASE_URL'], conn_max_age=600, ssl_require=True
    )  # NEW

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # NEW

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AI API Settings
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
AI_HORDE_API_KEY = os.environ.get('AI_HORDE_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')  # NEW

# Auth settings
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Security/Proxy headers for Render (behind proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # NEW
PRODUCTION = bool(os.environ.get('RENDER')) or not DEBUG  # NEW
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True' if PRODUCTION else 'False') == 'True'  # NEW
SESSION_COOKIE_SECURE = not DEBUG  # NEW
CSRF_COOKIE_SECURE = not DEBUG  # NEW

# CSRF trusted origins (comma-separated)
_csrf_origins = os.environ.get('CSRF_TRUSTED_ORIGINS', '')  # NEW
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]  # NEW
# Auto-add Render host if present
if RENDER_HOSTNAME:  # NEW
    domain = f"https://{RENDER_HOSTNAME}"
    if domain not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(domain)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
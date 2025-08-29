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
RENDER_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')  # CHANGED
if RENDER_HOSTNAME and RENDER_HOSTNAME not in ALLOWED_HOSTS:  # FIX block
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)

# NEW: CSRF trusted origins (from Render hostname or env)
_env_csrf = [o for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o]
if RENDER_HOSTNAME:  # FIX block
    _env_csrf.append(f"https://{RENDER_HOSTNAME}")
CSRF_TRUSTED_ORIGINS = _env_csrf or []

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
    'whitenoise.runserver_nostatic',  # NEW: ensure whitenoise controls static even in dev
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
if os.environ.get('DATABASE_URL'):  # FIX
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.parse(
            os.environ['DATABASE_URL'],
            conn_max_age=600,
            ssl_require=(os.environ.get('PGSSLMODE') == 'require' or not DEBUG)
        )
    except Exception:
        pass

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
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'

# Email configuration: console backend by default to avoid ConnectionRefused
# Only enable SMTP when all required vars are present.
_email_host = os.environ.get('EMAIL_HOST')
_email_user = os.environ.get('EMAIL_HOST_USER')
_email_pass = os.environ.get('EMAIL_HOST_PASSWORD')

if _email_host and _email_user and _email_pass:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = _email_host
    EMAIL_HOST_USER = _email_user
    EMAIL_HOST_PASSWORD = _email_pass
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', 10))
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', _email_user)
    SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
else:
    # Safe default: print emails to console/log; password reset won’t try SMTP
    EMAIL_BACKEND = os.environ.get(
        'EMAIL_BACKEND',
        'django.core.mail.backends.console.EmailBackend'
    )
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@localhost')
    SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
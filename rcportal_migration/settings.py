"""
Django settings for rcportal_migration project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j+(f2o=5r#%pu6v_ewjs$9w)rqa-(#+dvz69-npltu3!!_&1pl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATES = [
    {
        'OPTIONS': {
            'debug': DEBUG,
        },
    },
]

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'crams',
    'rcallocation',
    'account',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rcportal_migration.urls'

WSGI_APPLICATION = 'rcportal_migration.wsgi.application'

DATABASE_ROUTERS = ['crams.crams_router.CramsRouter',
                    'rcallocation.rcallocation_router.RcallocationRouter',
                    'rcportal_migration.auth_router.AuthRouter',
                    'account.account_router.AccountRouter']

# Custom User model
AUTH_USER_MODEL = 'account.User'


# Database Names
CRAMS_DB = 'crams_empty'
NECTAR_DB = 'crams_prod'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    # Default Database, not used but leave as default
    'default': {},

    # CRAMS Database
    CRAMS_DB: {
        'NAME': CRAMS_DB,
        'ENGINE': 'django.db.backends.mysql',  # django.db.backends.postgresql_psycopg2
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # leave empty for localhost
        'PORT': ''  # leave empty for default
    },

    # NeCTAR Database
    NECTAR_DB: {
        'NAME': NECTAR_DB,
        'ENGINE': 'django.db.backends.mysql',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # leave empty for localhost
        'PORT': ''  # leave empty for default
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    )
}


# Import the local_settings.py to override some of the default settings, like database settings
try:
    from rcportal_migration.local.local_settings import *
except ImportError:
    logging.warning("No local_settings file found.")

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR + '/log/migration.log',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.db': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'crams': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

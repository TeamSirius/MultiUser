"""
Django settings for MultiUser project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""


try:
    from secret import *
except ImportError:
    # This configuration allows us to use environment variables for Heroku
    #   while still being able to use sqlite on our dev machines
    import os
    import dj_database_url
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if SECRET_KEY is None:
        msg = 'Check your configuration. No secret.py and no SECRET_KEY environment variable.'
        raise Exception(msg)
    default_db = 'sqlite:////{}'.format(os.path.join(BASE_DIR, 'db.sqlite3'))
    DATABASES = {
        'default': dj_database_url.config(default=default_db)
    }

    GCM_APIKEY = os.environ.get('GCM_APIKEY')

    if GCM_APIKEY is None:
        raise Exception('Can\'t find GCM key')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'tastypie',
    'marauder',
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

ROOT_URLCONF = 'MultiUser.urls'

WSGI_APPLICATION = 'MultiUser.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

TASTYPIE_DEFAULT_FORMATS = ['json']

# Python Social Auth Additions

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.Facebook2OAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS += (
    'social.apps.django_app.default',
)

SOCIAL_AUTH_FACEBOOK_SCOPE = ['user_friends']

# Django GCM Setup
# https://github.com/bogdal/django-gcm

INSTALLED_APPS += (
    'gcm',
)

GCM_DEVICE_MODEL = 'marauder.models.UserDevice'

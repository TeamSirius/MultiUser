"""
Django settings for MultiUser project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os

try:
    from secret import *
except ImportError:
    # This configuration allows us to use environment variables for Heroku
    #   while still being able to use sqlite on our dev machines
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

    # Get information for Android Push Notifications
    GCM_APIKEY = os.environ.get('GCM_APIKEY')

    if GCM_APIKEY is None:
        raise Exception('Can\'t find GCM key')

    # Determine if we should use S3 Buckets or not
    USE_S3 = os.environ.get('USE_S3', False)
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

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

# S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
# S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
# S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
# S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
# Static files (CSS, JavaScript, Images) # https://docs.djangoproject.com/en/1.7/howto/static-files/
# Determine if we should use S3 to serve static files or not
if USE_S3:
    INSTALLED_APPS += ('storages',)
    AWS_STORAGE_BUCKET_NAME = S3_BUCKET_NAME
    AWS_ACCESS_KEY_ID = S3_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY = S3_SECRET_KEY
    AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(S3_BUCKET_NAME)

    STATICFILES_LOCATION = 'static'
<<<<<<< Updated upstream
    STATICFILES_STORAGE = 'MultiUser.custom_storages.StaticStorage'
    STATIC_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN,
                                         STATICFILES_LOCATION)

    MEDIAFILES_LOCATION = 'media'
    MEDIA_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN,
                                        MEDIAFILES_LOCATION)
    DEFAULT_FILE_STORAGE = 'MultiUser.custom_storages.MediaStorage'
    STATICFILES_STORAGE = 'MultiUser.storages.StaticStorage'
    STATIC_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN,
                                         STATICFILES_LOCATION)
=======
    STATICFILES_STORAGE = 'MultiUser.storages.StaticStorage'
    STATIC_URL = 'https://{}/{}/'.format(AWS_S3_CUSTOM_DOMAIN,
                                         STATICFILES_LOCATION)

>>>>>>> Stashed changes
else:
    STATIC_URL = '/static/'
    STATIC_ROOT = 'staticfiles'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

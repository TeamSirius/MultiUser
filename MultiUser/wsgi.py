"""
WSGI config for MultiUser project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MultiUser.settings")

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise
from django.conf import settings

application = get_wsgi_application()

if not settings.USE_S3:
    application = DjangoWhiteNoise(application)

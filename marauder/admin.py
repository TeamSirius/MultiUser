from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from tastypie.models import create_api_key


from .models import Floor, Location, AccessPoint

admin.site.register(Floor)

admin.site.register(Location)

admin.site.register(AccessPoint)

models.signals.post_save.connect(create_api_key, sender=User)

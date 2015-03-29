# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marauder', '0007_userdevice'),
    ]

    # WARNING LOOK HERE:
    # This is a known bug in Django:
    # https://code.djangoproject.com/ticket/23740
    # The operation is here to show what is done, but
    # YOU MUST FAKE THIS MIGRATION
    operations = [
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([]),
        ),
    ]

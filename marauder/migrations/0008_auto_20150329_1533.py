# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marauder', '0007_userdevice'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([]),
        ),
    ]

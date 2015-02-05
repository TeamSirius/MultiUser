# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marauder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesspoint',
            name='temp_id',
            field=models.IntegerField(default=0, help_text=b'The ID of the item in the old database. Used for transitioning'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='floor',
            name='temp_id',
            field=models.IntegerField(default=9, help_text=b'The ID of the item in the old database. Used for transitioning'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='temp_id',
            field=models.IntegerField(default=0, help_text=b'The ID of the item in the old database. Used for transitioning'),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marauder', '0002_auto_20150204_2346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesspoint',
            name='temp_id',
            field=models.IntegerField(help_text=b'The ID of the item in the old database. Used for transitioning', null=True),
            preserve_default=True,
        ),
    ]

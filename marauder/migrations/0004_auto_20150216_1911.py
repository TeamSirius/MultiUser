# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marauder', '0003_auto_20150216_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floor',
            name='temp_id',
            field=models.IntegerField(help_text=b'The ID of the item in the old database. Used for transitioning', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='location',
            name='temp_id',
            field=models.IntegerField(help_text=b'The ID of the item in the old database. Used for transitioning', null=True),
            preserve_default=True,
        ),
    ]

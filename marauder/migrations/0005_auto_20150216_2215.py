# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marauder', '0004_auto_20150216_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floor',
            name='image',
            field=models.ImageField(height_field=b'image_height', width_field=b'image_width', upload_to=b'floormaps', blank=True, help_text=b'The image of the floor map for this floor', null=True),
            preserve_default=True,
        ),
    ]

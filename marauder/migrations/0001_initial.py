# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mac_address', models.CharField(help_text=b'The MAC Address of the Access Point', max_length=17)),
                ('signal_strength', models.FloatField(help_text=b'The average RSS of the Access Point')),
                ('standard_deviation', models.FloatField(help_text=b'The standard deviation of the seen RSS values')),
                ('recorded', models.DateTimeField(help_text=b'When this access point was recorded')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Floor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('building_name', models.CharField(help_text=b'The name of the building', max_length=255)),
                ('floor_number', models.IntegerField(help_text=b'The floor number')),
                ('image_width', models.IntegerField(help_text=b"The width of the image in the 'image' field", null=True, blank=True)),
                ('image_height', models.IntegerField(help_text=b"The height of the image in the 'image' field", null=True, blank=True)),
                ('image', models.ImageField(height_field=b'image_height', width_field=b'image_width', upload_to=b'', blank=True, help_text=b'The image of the floor map for this floor', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(help_text=b'The short name for the location', max_length=15)),
                ('verbose_name', models.CharField(help_text=b'The user meaningful name for the location', max_length=255)),
                ('x_coordinate', models.IntegerField(help_text=b'The X coordinate on the image')),
                ('y_coordinate', models.IntegerField(help_text=b'The Y coordinate on the image')),
                ('direction', models.IntegerField(help_text=b'The direction, in degrees, that this was recorded facing')),
                ('floor', models.ForeignKey(help_text=b'The building and floor that this location belongs to', to='marauder.Floor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set([('short_name', 'direction')]),
        ),
        migrations.AlterUniqueTogether(
            name='floor',
            unique_together=set([('building_name', 'floor_number')]),
        ),
        migrations.AddField(
            model_name='accesspoint',
            name='location',
            field=models.ForeignKey(help_text=b'The location that this AP belongs to', to='marauder.Location'),
            preserve_default=True,
        ),
    ]

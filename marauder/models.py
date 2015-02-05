from django.db import models


class Floor(models.Model):
    # TODO: Remove blank=True and null=True from all fields
    # TODO: Collect images and upload them to the database

    building_name = models.CharField(max_length=255,
                                     help_text='The name of the building')

    floor_number = models.IntegerField(help_text='The floor number')

    image_width = models.IntegerField(help_text="The width of the image in the 'image' field",
                                      blank=True,
                                      null=True)

    image_height = models.IntegerField(help_text="The height of the image in the 'image' field",
                                       blank=True,
                                       null=True)

    image = models.ImageField(help_text='The image of the floor map for this floor',
                              width_field='image_width',
                              height_field='image_height',
                              blank=True,
                              null=True)

    # TODO: Delete this post transition
    temp_id = models.IntegerField(help_text='The ID of the item in the old database. Used for transitioning')


    def __str__(self):
        return "{} Floor {}".format(self.building_name, self.floor_number)

    class Meta:
        unique_together = ('building_name', 'floor_number')


class Location(models.Model):

    short_name = models.CharField(max_length=15,
                                  help_text='The short name for the location')

    verbose_name = models.CharField(max_length=255,
                                    help_text='The user meaningful name for the location')

    x_coordinate = models.IntegerField(help_text='The X coordinate on the image')

    y_coordinate = models.IntegerField(help_text='The Y coordinate on the image')

    direction = models.IntegerField(help_text='The direction, in degrees, that this was recorded facing')

    floor = models.ForeignKey(Floor,
                              help_text='The building and floor that this location belongs to')

    # TODO: Delete this post transition
    temp_id = models.IntegerField(help_text='The ID of the item in the old database. Used for transitioning')


    def __str__(self):
        return self.verbose_name

    class Meta:
        unique_together = ('short_name', 'direction')


class AccessPoint(models.Model):
    mac_address = models.CharField(max_length=17,
                                   help_text='The MAC Address of the Access Point')

    signal_strength = models.FloatField(help_text='The average RSS of the Access Point')

    standard_deviation = models.FloatField(help_text='The standard deviation of the seen RSS values')

    recorded = models.DateTimeField(help_text='When this access point was recorded')

    location = models.ForeignKey(Location,
                                 help_text='The location that this AP belongs to')

    # TODO: Delete this post transition
    temp_id = models.IntegerField(help_text='The ID of the item in the old database. Used for transitioning')

    def __str__(self):
        return "{} -- {}".format(self.location, self.mac_address)

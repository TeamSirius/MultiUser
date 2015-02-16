import re
from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import (BaseUserManager,
                                        AbstractBaseUser,
                                        PermissionsMixin)
from django.utils.http import urlquote
from django.core import validators
from django.core.mail import send_mail


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
    temp_id = models.IntegerField(null=True,
                                  help_text='The ID of the item in the old database. Used for transitioning')


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
    temp_id = models.IntegerField(null=True,
                                  help_text='The ID of the item in the old database. Used for transitioning')


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
    temp_id = models.IntegerField(null=True,
                                  help_text='The ID of the item in the old database. Used for transitioning')

    def __str__(self):
        return "{} -- {}".format(self.location, self.mac_address)


# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(max_length=255,
#                               unique=True,
#                               help_text="The user's email address")
#
#     username = models.CharField('username', max_length=30, unique=True,
#                                 help_text='Required. 30 Characters or less. Letters, numbers, and @/./+/-/_ characters',
#                                 validators=[
#                                     validators.RegexValidator(re.compile('^[\w.@+-]+$'), 'Enter a valid username', 'invalid')
#                                 ])
#
#     full_name = models.CharField('full name', max_length=254)
#
#     short_name = models.CharField('short name', max_length=30)
#
#     is_staff = models.BooleanField('staff status', default=False,
#                                    help_text='Whether the user can use the admin site')
#
#     is_active = models.BooleanField('active', default=False,
#                                     help_text='Whether the user is active')
#
#     date_joined = models.DateTimeField('date joined',
#                                        default=now())
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', 'full_name', 'short_name']
#
#
#     class Meta:
#         verbose_name = 'user'
#         verbose_name_plural = 'users'
#
#     def __unicode__(self):
#         return self.full_name
#
#     def get_absolute_url(self):
#         return '/users/{}/'.format(urlquote(self.username))
#
#     def get_full_name(self):
#         return self.full_name.strip()
#
#     def get_short_name(self):
#         return self.short_name.strip()
#
#     def email_user(self, subject, message, from_email=None):
#         send_mail(subject, message, from_email, [self.email])

from django.conf.urls import url
from tastypie.resources import Resource
from tastypie.authentication import ApiKeyAuthentication
from tastypie import fields
from .api import CommonMeta
from .models import Floor
import json
from kNN import kNN
from django.db import connection
from .models import Floor

# Most stuff from here:
# http://stackoverflow.com/questions/20933214/creating-a-tastypie-resource-for-a-singleton-non-model-object
# http://django-tastypie.readthedocs.org/en/latest/non_orm_data_sources.html


class LocateMeObject(object):

    """ Represents a computed location
        Could very possibly be replaced with a Model instance in the future.
    """

    def __init__(self, **kwargs):
        self.__dict__['_data'] = {}
        if kwargs:
            self.update(kwargs)

    def __getattr__(self, name):
        return self._data.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__['_data'][name] = value

    def update(self, other):
        for key in other:
            self.__setattr__(key, other[key])

    def to_dict(self):
        return self._data


class LocateMeResource(Resource):

    """ The API to compute a location from known access points
        Subclasses from Resource and not ModelResource because we need to
            transform data from one type to another
    """

    building_name = fields.CharField(
        attribute='building_name',
        help_text='The name of the building you\'re in')

    floor_number = fields.IntegerField(attribute='floor_number',
                                       help_text='The floor you\'re on')

    x_coordinate = fields.IntegerField(
        attribute='x_coordinate',
        help_text='The x coordinate on the image')

    y_coordinate = fields.IntegerField(
        attribute='y_coordinate',
        help_text='The y coordinate on the image')

    class Meta(CommonMeta):
        resource_name = 'user_location'
        fields = ['building_name', 'floor_number',
                  'x_coordinate', 'y_coordinate']
        allowed_methods = ['post']

    def _save_user_location(user, location):
        """ Will be used to attach the location to the given user.
        Currently, this does nothing because we don't have the
        location <-> user association yet """
        pass

    def _locate_user(access_points):
        """ Will use Brett's kNN algorithm with the list of access points to
        determine the location. Currently, returned a random location within
        Halligan"""
        # TODO: Don't return a random point

        # Determine the random point
        # Randomly choose a floor
        floor = random.choice(
            Floor.objects.filter(
                building_name__icontains='halligan'))

        # Randomly choose a location on that floor
        location = random.choice(floor.location_set())

        # Convert information to a location object
        location_object = LocateMeObject()
        location_object.building_name = floor.building_name
        location_object.floor_number = floor.floor_number
        location_object.x_coordinate = location.x_coordinate
        location_object.y_coordinate = location.y_coordinate

        return location_object

    def _notify_user(user, message):
        pass

    def prepend_urls(self):
        find_friend_url = r'^(?P<resource_name>{})/friend/$'
        tell_friend_url = r'^(?P<resource_name>{})/tell/$'
        find_me_url = r'^(?P<resource_name>{})/me/$'
        return [
            url(find_friend_url.format(self._meta.resource_name),
                self.wrap_view('locate_friend'),
                name='locate_friend'),
            url(tell_friend_url.format(self._meta.resource_name),
                self.wrap_view('notify_friend'),
                name='notify_friend'),
            url(find_me_url.format(self._meta.resource_name),
                self.wrap_view('locate_me'),
                name='locate_me'),
        ]

    def locate_friend(self, request, **kwargs):
        # TODO:
        #   1) Get friend's ID from request body
        #   2) Ensure this user is actually friends with requested ID
        #        This means using the facebook API server side
        #        Could also have an allow list later on
        #   3) Send request for the location to the friend's phone
        pass

    def notify_friend(self, request, **kwargs):
        pass

    def locate_me(self, request, **kwargs):
        pass

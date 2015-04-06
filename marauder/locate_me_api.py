from django.conf.urls import url
from django.db import connection
from tastypie.resources import Resource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import (HttpAccepted, HttpForbidden,
                           HttpBadRequest, HttpNotFound)
from tastypie import fields
from social.apps.django_app.default.models import UserSocialAuth
from django.contrib.auth.models import User
from .models import Floor
from .kNN import kNN
import json
import facebook
import logging

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

    class Meta:
        resource_name = 'user_location'
        fields = ['building_name', 'floor_number',
                  'x_coordinate', 'y_coordinate']
        allowed_methods = ['post']
        always_return_data = True
        authentication = ApiKeyAuthentication()

    def _is_authorized(self, request):
        """Determine if the request is authorized to perform the action"""
        # TODO: Make this actually function
        return True

    def _save_user_location(self, user, location):
        """ Will be used to attach the location to the given user.
        Currently, this does nothing because we don't have the
        location <-> user association yet """
        pass

    def _locate_user(self, access_points):
        """ Will use Brett's kNN algorithm with the list of access points to
        determine the location. Currently, returned a random location within
        Halligan"""

        modified_aps = {ap['mac_address']: ap['signal_strength']
                        for ap in access_points}

        found, x_coord, y_coord, floor_id = kNN(connection.cursor(), modified_aps)

        if not found:
            msg = 'Could not locate you'
            raise ImmediateHttpResponse(HttpNotFound(msg))

        try:
            floor = Floor.objects.get(pk=floor_id)
        except Floor.DoesNotExist:
            msg = 'Could not locate you'
            raise ImmediateHttpResponse(HttpNotFound(msg))


        # Convert information to a location object
        location_object = LocateMeObject()
        location_object.building_name = floor.building_name
        location_object.floor_number = floor.floor_number
        location_object.x_coordinate = int(x_coord)
        location_object.y_coordinate = int(y_coord)
        location_object.image_url = floor.image.url

        return location_object

    def _notify_user(self, device, message):
        """Sends the message provided as a GCM push notification to all
        of the devices in device

        device can either be a single device or a queryset of devices
        """
        _, response = device.send_message(json.dumps(message))

        if response['failure'] == 1:
            # TODO: Log the failure
            # May change in the future to something more appropriate
            return HttpAccepted
        else:
            # TODO: Log the success
            return HttpAccepted

    def _verify(self, request):
        """Checks that the request should be allowed to go through.
        If not, raises an error and terminates the request"""
        self.method_check(request, allowed=self._meta.allowed_methods)
        self.is_authenticated(request)
        self._is_authorized(request)
        self.throttle_check(request)

    def base_urls(self):
        """Override the TastyPie URLs for this resource
            because we don't need them
        """
        find_friend_url = r'^(?P<resource_name>{})/friend/$'
        tell_friend_url = r'^(?P<resource_name>{})/respond/$'
        find_me_url = r'^(?P<resource_name>{})/me/$'
        return [
            url(find_friend_url.format(self._meta.resource_name),
                self.wrap_view('find_friend'),
                name='find_friend'),
            url(tell_friend_url.format(self._meta.resource_name),
                self.wrap_view('respond_to_request'),
                name='respond_to_request'),
            url(find_me_url.format(self._meta.resource_name),
                self.wrap_view('locate_me'),
                name='locate_me'),
        ]

    def find_friend(self, request, **kwargs):
        """An endpoint that allows a user to request the location of their friend

           Does not allow users to request the location of people they're not
           friends with on facebook.

           Does not allow users to request the location of people who do not
           have a phone registered to their account (for push notifications)
        """
        self._verify(request)
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('Content-Type',
                                                        'application/json'))
        # Was the Facebook ID of a friend supplied?
        friend_fb_id = data.get('friend_fb_id', None)
        if friend_fb_id is None:
            raise ImmediateHttpResponse(
                HttpBadRequest('Must specify a friend\'s FB ID'))

        # Does the requestor have a facebook account associated with their
        # profile?
        #
        # Should always be yes with the exception of the admin accounts
        my_user = request.user.social_auth.filter(provider='facebook')
        if not my_user.exists():
            raise ImmediateHttpResponse(
                HttpForbidden('Could not find you as a facebook user'))

        # Does the friend have an account in our system?
        try:
            friend_user = UserSocialAuth.objects.get(provider='facebook',
                                                     uid=friend_fb_id)
        except UserSocialAuth.DoesNotExist:
            msg = 'Could not find user with FB id {}'.format(friend_fb_id)
            raise ImmediateHttpResponse(HttpNotFound(msg))

        # Are the requestor and the requested friend *actually* friends?
        graph = facebook.GraphAPI(access_token=my_user.first().tokens)
        response = graph.get_object('/me/friends/{}'.format(friend_fb_id))
        if len(response['data']) == 0:
            msg = 'You can not request a location from that user'
            raise ImmediateHttpResponse(HttpForbidden(msg))

        # Does the friend have a phone associated with their profile?
        # This should also always be yes, with the exception of the admins
        friend_devices = friend_user.user.userdevice_set.all()
        if not friend_devices.exists():
            msg = 'Could not find friend with FB id {}'.format(friend_fb_id)
            raise ImmediateHttpResponse(HttpNotFound(msg))

        # Send the request for location to the friend
        msg_data = {
            'type': 'request_location',
            'requestor': request.user.get_full_name(),
            'requestor_id': request.user.pk
        }

        response_class = self._notify_user(friend_devices, msg_data)
        return self.create_response(request, data={},
                                    response_class=response_class)

    def respond_to_request(self, request, **kwargs):
        """Allows a user to respond to a request for their location"""
        self._verify(request)
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('Content-Type',
                                                        'application/json'))
        allow_request = data.get('allow_request', None)
        requestor_id = data.get('requestor_id', None)
        access_points = data.get('access_points', None)
        if allow_request is None or requestor_id is None:
            msg = 'Need both allow_request and requestor_id'
            raise ImmediateHttpResponse(HttpBadRequest(msg))
        if allow_request and access_points is None or len(access_points) < 1:
            msg = 'If allow_request, then access_points must be provided'
            raise ImmediateHttpResponse(HttpBadRequest(msg))

        # Make sure the requestor actually exists
        try:
            requestor = User.objects.get(pk=requestor_id)
            requestor_device_set = requestor.userdevice_set.all()
        except User.DoesNotExist:
            msg = 'Could not find User with id {}'.format(requestor_id)
            raise ImmediateHttpResponse(HttpNotFound(msg))

        # And also make sure the requestor has a phone
        if not requestor_device_set.exists():
            msg = 'Could not find User with id {}'.format(requestor_id)
            raise ImmediateHttpResponse(HttpNotFound(msg))

        if allow_request:
            location = self._locate_user(access_points)
            self._save_user_location(request.user, location)

            msg = {
                'type': 'request_granted',
                'friend': request.user.get_full_name(),
                'building_name': location.building_name,
                'floor_number': location.floor_number,
                'x_coordinate': location.x_coordinate,
                'y_coordinate': location.y_coordinate,
                'friend_id': request.user.pk,
                'image_url': location.image_url,
            }
        else:
            msg = {
                'type': 'request_denied',
                'friend': request.user.get_full_name(),
                'friend_id': request.user.pk
            }

        response_class = self._notify_user(requestor_device_set, msg)
        return self.create_response(request, data={},
                                    response_class=response_class)

    def locate_me(self, request, **kwargs):
        """Used by a user to locate themselves within a building"""
        self._verify(request)
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('Content-Type',
                                                        'application/json'))

        access_points = data.get('access_points', None)
        if access_points is None or len(access_points) < 1:
            msg = 'No access points provided'
            raise ImmediateHttpResponse(HttpBadRequest(msg))

        location = self._locate_user(access_points)
        self._save_user_location(request.user, location)

        return self.create_response(request,
                                    data=location.to_dict(),
                                    response_class=HttpAccepted)

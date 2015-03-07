from tastypie.resources import Resource
from tastypie import fields
from .api import CommonMeta
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


    building_name = fields.CharField(attribute='building_name',
                                     help_text='The name of the building you\'re in')

    floor_number = fields.IntegerField(attribute='floor_number',
                                       help_text='The floor you\'re on')

    x_coordinate = fields.IntegerField(attribute='x_coordinate',
                                       help_text='The x coordinate on the image')

    y_coordinate = fields.IntegerField(attribute='y_coordinate',
                                       help_text='The y coordinate on the image')

    class Meta(CommonMeta):
        resource_name = 'locateme'
        fields = ['building_name', 'floor_number',
                  'x_coordinate', 'y_coordinate']
        allowed_methods = ['post']

    def detail_uri_kwargs(self, bundle_or_obj):
        """ Used for looking up objects, but we don't do that, so empty """
        kwargs = {}
        return kwargs

    def obj_create_list(self, bundle, **kwargs):
        """ This won't ever create a list of objects, so delegate to creating just one"""
        return [self.obj_create(bundle, **kwargs)]

    def obj_create(self, bundle, **kwargs):
        """ Compute a location from a list of known access points"""
        access_points = json.loads(bundle.request.body)

        (x, y, floor_id) = kNN(access_points['objects'], db_cursor=connection.cursor())
        floor = Floor.objects.get(pk=floor_id)
        
        locate_me = LocateMeObject()
        locate_me.building_name = floor.building_name
        locate_me.floor_number = floor.floor_number
        locate_me.x_coordinate = x
        locate_me.y_coordinate = y

        bundle.obj = locate_me
        bundle = self.full_hydrate(bundle)

        return bundle

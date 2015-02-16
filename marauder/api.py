from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from .models import Floor, Location, AccessPoint
from .authorizations import SiriusAuthorization, AuthenticateForPost


class MultipartResource(object):
    def deserialize(self, request, data, format=None):
        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')
        if format == 'application/x-www-form-urlencoded':
            return request.POST
        if format.startswith('multipart'):
            data = request.POST.copy()
            # data = super(MultipartResource, self).deserialize(request,
            #                                                   data,
            #                                                   format)
            data.update(request.FILES)
            return data
        return super(MultipartResource, self).deserialize(request, data, format)


class CommonMeta:
    """ Specify a few common attributes for resources """
    limit = 0
    authorization = SiriusAuthorization()
    authentication = AuthenticateForPost()
    always_return_data = True


class FloorResource(MultipartResource, ModelResource):
    """ The resource for a Floor
        Allows filtering on building_name and floor_number
    """

    image = fields.FileField(attribute='image', null=True, blank=True)

    class Meta(CommonMeta):
        queryset = Floor.objects.all()
        fields = ['building_name', 'floor_number', 'image_width',
                  'image_height', 'image']

        filtering = {
            'building_name': ALL,
            'floor_number': ALL,
        }


class LocationResource(ModelResource):
    """ The resource for a location
        Allows filtering on short_name, verbose_name, x and y coordinates,
        and the associated floor
    """

    floor = fields.ForeignKey(FloorResource, 'floor')

    class Meta(CommonMeta):
        queryset = Location.objects.all()
        fields = ['short_name', 'verbose_name', 'x_coordinate', 'y_coordinate',
                  'direction', 'floor']

        filtering = {
            'short_name': ALL,
            'verbose_name': ALL,
            'x_coordinate': ALL,
            'y_coordinate': ALL,
            'floor': ALL_WITH_RELATIONS
        }


class AccessPointResource(ModelResource):
    """ The resource for an access point.
        Allows filtering on mac_address and the associated location
    """

    location = fields.ForeignKey(LocationResource, 'location')

    class Meta(CommonMeta):
        queryset = AccessPoint.objects.all()
        fields = ['mac_address', 'signal_strength', 'standard_deviation',
                  'recorded', 'location']

        filtering = {
            'mac_address': ALL,
            'location': ALL_WITH_RELATIONS
        }

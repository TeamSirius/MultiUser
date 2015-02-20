from django.conf.urls import patterns, include, url
from tastypie.api import Api
from .api import FloorResource, LocationResource, AccessPointResource
from .locate_me_api import LocateMeResource

v1_api = Api(api_name='v1')
v1_api.register(FloorResource())
v1_api.register(LocationResource())
v1_api.register(AccessPointResource())
v1_api.register(LocateMeResource())


urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
)

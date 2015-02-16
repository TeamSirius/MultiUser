from django.conf.urls import patterns, include, url
from tastypie.api import Api
from .api import FloorResource, LocationResource, AccessPointResource

v1_api = Api(api_name='v1')
v1_api.register(FloorResource())
v1_api.register(LocationResource())
v1_api.register(AccessPointResource())


urlpatterns = patterns('',
    url(r'^api/', include(v1_api.urls)),
)

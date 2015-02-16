from tastypie.authorization import ReadOnlyAuthorization
from tastypie.authentication import BasicAuthentication


class SiriusAuthorization(ReadOnlyAuthorization):
    """ Only allow superusers to post data """

    def create_list(self, object_list, bundle):
        if bundle.request.user.is_superuser:
            return object_list
        else:
            return []

    def create_detail(self, object_list, bundle):
        return True


class AuthenticateForPost(BasicAuthentication):
    """ Require auth for POST but nothing else """

    def is_authenticated(self, request, **kwargs):
        if request.method == "POST":
            return super(AuthenticateForPost, self).is_authenticated(request,
                                                                      **kwargs)
        else:
            return True

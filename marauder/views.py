from django.http import HttpResponse
from django.contrib.auth import login
from social.apps.django_app.utils import psa
from social.apps.django_app.default.models import UserSocialAuth
import json


# Define an URL entry to point to this view, call it passing the
# access_token parameter like ?access_token=<token>. The URL entry must
# contain the backend, like this:
#
#   url(r'^register-by-token/(?P<backend>[^/]+)/$',
#       'register_by_access_token')

@psa('social:complete')
def register_by_access_token(request, backend='facebook'):
    # This view expects an access_token GET parameter, if it's needed,
    # request.backend and request.strategy will be loaded with the
    # current backend and strategy.
    token = request.GET.get('access_token')
    user = request.backend.do_auth(token)
    print user
    if user:
        response = {
            'username': user.username,
            'api_key': user.api_key.key
        }
        return HttpResponse(json.dumps(response))
    else:
        return HttpResponse(500)


def request_location(request):
    other_user = request.GET.get('friend_id')

    try:
        usa = UserSocialAuth.objects.get(uid=other_user)
        device = usa.user.userdevice_set.first()

        if device is None:
            return HttpResponse(404)

        msg = {
            'type': 'request_location',
            'requestor': 'Tyler Lubeck'
        }
        device.send_message(json.dumps(msg))
        return HttpResponse(200)

    except UserSocialAuth.DoesNotExist:
        return HttpResponse(404)

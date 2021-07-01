import pytz

from django.utils import timezone
from website.models import Profile

# make sure you add `TimezoneMiddleware` appropriately in settings.py
class TimezoneMiddleware(object):
    """
    Middleware to properly handle the users timezone
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # make sure they are authenticated so we know we have their tz info.
        if request.user.is_authenticated:
            # we are getting the users timezone that in this case is stored in 
            # a user's profile
            tz_str = request.user
            tz_str=tz_str.id
            tz_str=Profile.objects.get(user=tz_str)
            timezone.activate(pytz.timezone(tz_str.timezone))
        # otherwise deactivate and the default time zone will be used anyway
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
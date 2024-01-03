from rest_framework.throttling import SimpleRateThrottle

class FriendRequestRateThrottle(SimpleRateThrottle):
    scope = 'friend_request'
    rate = '3/min'  # Define the rate

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
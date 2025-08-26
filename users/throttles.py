from rest_framework.throttling import SimpleRateThrottle


class ResetPasswordRateThrottle(SimpleRateThrottle):
    scope = 'reset_password'

    def get_cache_key(self, request, view):
        email = request.data.get('email')
        ident = self.get_ident(request)
        if not email:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': f'{ident}:{email}'
        }

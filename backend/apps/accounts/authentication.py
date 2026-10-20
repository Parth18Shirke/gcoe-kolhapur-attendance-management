from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from .models import UserToken

class TokenAuthentication(BaseAuthentication):
    """
    Custom Bearer Token authentication based on revocable UserToken model.
    Header format: `Authorization: Bearer <64-char-hex-token>` or `Authorization: Token <token>`
    """
    keyword = 'Bearer'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            return None

        prefix, token_key = parts[0], parts[1]
        if prefix.lower() not in ['bearer', 'token']:
            return None

        try:
            token = UserToken.objects.select_related('user').get(key=token_key)
        except UserToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid authentication token.')

        if not token.is_valid():
            raise exceptions.AuthenticationFailed('Authentication token has expired.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled.')

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword

class TokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'apps.accounts.authentication.TokenAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'Token',
            'description': 'Custom Bearer token issued upon OTP verification.',
        }

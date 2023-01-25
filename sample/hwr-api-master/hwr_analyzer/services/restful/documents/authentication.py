from drf_spectacular.extensions import OpenApiAuthenticationExtension


class AuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'utils.authentications.simple_authentication.SimpleAuthentication'  # full import path OR class ref
    name = 'AuthenticationScheme'  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }

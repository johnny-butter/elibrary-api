import jwt
from ninja.security import HttpBearer
from django.conf import settings


class AuthJWT(HttpBearer):

    def authenticate(self, _, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        except jwt.exceptions.DecodeError:
            raise ValueError('Wrong token value')

        return payload

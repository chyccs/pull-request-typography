from rest_framework import status

from utils.exceptions import BaseAPIException


class UnauthorizedError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = 'Unauthorized.'
    code = 'UNAUTHORIZED'


class InvalidSignatureError(UnauthorizedError):
    message = 'Invalid signature.'
    code = 'INVALID_SIGNATURE'

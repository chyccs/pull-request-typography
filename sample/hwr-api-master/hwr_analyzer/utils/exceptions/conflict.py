from rest_framework import status

from utils.exceptions import BaseAPIException


class ConflictError(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    message = 'Conflict.'
    code = 'CONFLICT'

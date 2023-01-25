from typing import Type

from django.db import models
from rest_framework import status

from utils.exceptions import BaseAPIException


class NotFoundError(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    message = 'Not found.'
    code = 'NOT_FOUND'


class ObjectNotFoundError(NotFoundError):
    message = 'Object not found.'
    code = 'NOT_FOUND'

    def __init__(self, model: Type[models.Model], *args, **kwargs):
        if not kwargs.get('message'):
            kwargs['message'] = f"{model.__name__} object not found."
        super().__init__(*args, **kwargs)

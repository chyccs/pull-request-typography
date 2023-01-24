from rest_framework import status

from utils.exceptions import BaseAPIException
from utils.response import APIResponse


class BadRequestError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = 'Bad request.'
    code = 'BAD_REQUEST'


class InvalidParamError(BadRequestError):
    message = 'Invalid parameter.'
    code = APIResponse.Code.INVALID_PARAM.value


class InvalidFileTypeError(BadRequestError):
    code = 'INVALID_FILE_TYPE'

    def __init__(self, *allowed_types, **kwargs):
        message = f"Allowed types : {', '.join(allowed_types)}."
        super().__init__(message=message, **kwargs)


class InvalidFileRefError(BadRequestError):
    code = 'INVALID_FILE_REF'


class DuplicatedFileRefError(BadRequestError):
    code = 'FILE_REF_DUPLICATION'


class FileSizeLimitExceededError(BadRequestError):
    code = 'FILE_SIZE_LIMIT_EXCEEDED'


class FileNameTooLongError(BadRequestError):
    code = 'FILE_NAME_TOO_LONG'


class DecodeError(BadRequestError):
    message = 'Fail to decode.'
    code = 'DECODE_ERROR'

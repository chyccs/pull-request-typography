from typing import Optional

from django.core import exceptions as django_exceptions
from rest_framework import exceptions as drf_exceptions
from rest_framework.views import (
    exception_handler,
    set_rollback,
)

from utils import exceptions as base_exceptions
from utils.response import (
    APIErrorResponse,
    ErrorData,
)


def _convert_to_manageable(exc):
    if isinstance(exc, (drf_exceptions.AuthenticationFailed, drf_exceptions.NotAuthenticated)):
        return base_exceptions.UnauthorizedError(
            message=str(exc),
            title='인증에 실패하였습니다.',
            description='인증이 필요한 작업입니다.',
        )
    if isinstance(exc, (django_exceptions.PermissionDenied, drf_exceptions.PermissionDenied)):
        return base_exceptions.ForbiddenError(
            message=str(exc),
            title='권한이 없습니다.',
            description='권한이 필요한 작업입니다.',
        )
    return exc


def _base_exception_handler(exc, _context) -> Optional[APIErrorResponse]:
    if not isinstance(exc, base_exceptions.BaseAPIException):
        return None
    return APIErrorResponse(
        status=exc.status_code,
        message=exc.message,
        error=exc.error,
    )


def custom_exception_handler(exc, context) -> Optional[APIErrorResponse]:
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    _exc = _convert_to_manageable(exc)
    response = exception_handler(_exc, context)
    if response:
        return APIErrorResponse(
            status=_exc.status_code,
            message="APIException: " + str(_exc.detail),
            error=ErrorData(
                title=base_exceptions.InternalServerError.title,
                description=base_exceptions.InternalServerError.description,
                code=str(_exc.default_code).upper()),
        )

    set_rollback()

    if _response := _base_exception_handler(_exc, context):
        return _response

    return APIErrorResponse(
        message='Internal Server Error',
        error=base_exceptions.InternalServerError.default_error_object(),
    )

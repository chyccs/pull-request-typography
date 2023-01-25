from enum import (
    Enum,
    unique,
)
from typing import (
    Any,
    Dict,
    Optional,
    Union,
)

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


def _remove_none_values(data):
    return {k: v for k, v in data.items() if v is not None}


class APIResponse(Response):
    @unique
    class Code(Enum):
        ALREADY_EXIST = 'ALREADY_EXIST'
        NOT_EXIST = 'NOT_EXIST'
        INVALID_PARAM = 'INVALID_PARAM'
        INVALID_STATE = 'INVALID_STATE'
        TRANSFER_BLOCKED = 'TRANSFER_BLOCKED'
        ORDER_BLOCKED = 'ORDER_BLOCKED'
        INSUFFICIENT_DABS = 'INSUFFICIENT_DABS'
        INSUFFICIENT_FUNDS = 'INSUFFICIENT_FUNDS'
        SUBSCRIPTION_LIMIT_EXCEEDED = 'SUBSCRIPTION_LIMIT_EXCEEDED'
        QUOTA_EXCEEDED = 'QUOTA_EXCEEDED'
        DISAGREED_REQUIRED_TERMS = 'DISAGREED_REQUIRED_TERMS'
        INVALID_DABS_CODE = 'INVALID_DABS_CODE'
        INVALID_VERIFY_CODE = 'INVALID_VERIFY_CODE'
        EXPIRED_VERIFY_LIMIT = 'EXPIRED_VERIFY_LIMIT'
        EXCEED_REQUEST_LIMIT = 'EXCEED_REQUEST_LIMIT'
        IDENTITY_VERIFICATION_ERROR = 'IDENTITY_VERIFICATION_ERROR'
        VERIFIED_TOKEN = 'VERIFIED_TOKEN'
        EXPIRED_TOKEN = 'EXPIRED_TOKEN'
        UNKNOWN_RESOURCE = 'UNKNOWN_RESOURCE'
        INVALID_INDIVIDUAL_INFO = 'INVALID_INDIVIDUAL_INFO'
        INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR'

        def __str__(self):
            return self.value

    def __init__(self, status=None, *, message=None, code=None, data=None, headers=None, **kargs):
        code = code.value if isinstance(code, APIResponse.Code) else code
        payload = {
            'result': message,
            'code': code,
            'contents': data,
        }

        if kargs:
            payload.update(kargs)

        super().__init__(_remove_none_values(payload), status=status, headers=headers)


class ErrorData(dict):
    def __init__(self, title: str, description: str, code='UNDEFINED_CODE', data=None):
        code = code.value if isinstance(code, APIResponse.Code) else code
        super().__init__(title=title, description=description, code=code, data=data)

    @property
    def title(self):
        return self['title']

    @property
    def description(self):
        return self['description']

    @description.setter
    def description(self, v):
        self['description'] = v

    @property
    def code(self):  # TODO: Deprecated code in ErrorData
        return self['code']

    @property
    def data(self):
        return self['data']


class APIErrorResponse(Response):
    def __init__(
        self,
        status: int = HTTP_500_INTERNAL_SERVER_ERROR,
        error: Union[ErrorData, Dict[Any, Any], None] = None,
        *,
        message: Optional[str] = None,
        headers=None,
    ):
        payload = {
            'result': message,
            'code': getattr(error, 'code', None),
            'error': error,
            'contents': error,
        }

        super().__init__(_remove_none_values(payload), status=status, headers=headers)


class APIPaginationResponse(APIResponse):
    """Build pagination response.

    The `pagination_data` is a dict and should conform to following schema:

        {
            'offset': number,
            'limit': number,
            'count': number, # total number of rows
            'items': queryset or array,
        }

        - or -

        {
            'nextCursor': base64-encoded string,
            'limit': number,
            'items': queryset or array,
        }
    """

    def __init__(self, pagination_data, status=HTTP_200_OK, *, message=None):
        super().__init__(status, message=message, data=pagination_data)

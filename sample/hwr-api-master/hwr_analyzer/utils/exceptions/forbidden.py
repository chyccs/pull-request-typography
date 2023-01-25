from rest_framework import status

from utils.exceptions import BaseAPIException


class ForbiddenError(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    message = 'Forbidden.'
    code = 'FORBIDDEN'


class InvalidAccessError(ForbiddenError):
    code = 'INVALID_ACCESS'
    title = '잘못된 경로로 접근하셨습니다.'
    description = ('비정상적인 경로로 접근하셨거나 오류가 발생해 요청을 수행할 수 없습니다. '
                   '확인하신 후 다시 시도해주세요. 불편을 드려 죄송합니다.')

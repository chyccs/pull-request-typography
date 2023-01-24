from rest_framework import status

from utils.exceptions import BaseAPIException


class InternalServerError(BaseAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = 'Internal server error.'
    code = 'INTERNAL_SERVER_ERROR'
    title = '오류가 발생했습니다.'
    description = '알 수 없는 오류가 발생했습니다.'

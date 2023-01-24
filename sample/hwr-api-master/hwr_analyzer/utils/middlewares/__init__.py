from django.http import JsonResponse

from ..exceptions import BaseAPIException
from ..exceptions.handlers import custom_exception_handler


def build_response(data, status_code):
    return JsonResponse(data=data,
                        status=status_code,
                        json_dumps_params={'ensure_ascii': False})


class ExceptionHandlerMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, BaseAPIException):
            error_response = custom_exception_handler(exception, None)
            return build_response(data=error_response.data, status_code=error_response.status_code)
        return None

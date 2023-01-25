from utils.exceptions import BaseAPIException
from utils.exceptions.handlers import custom_exception_handler
from utils.middlewares import build_response


def catch_middleware_exception(func):
    def wraps(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseAPIException as e:
            r = custom_exception_handler(e, None)
            return build_response(data=r.data, status_code=r.status_code)
    return wraps

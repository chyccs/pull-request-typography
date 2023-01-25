from .base import APP_ENV
from .base import BASE_DIR
from .env import ENV


ROLLBAR = {
    'access_token': ENV.str('ROLLBAR_ACCESS_TOKEN', '9fca8c0766a04bbba90f8988853a9c16'),
    'environment': APP_ENV,
    'code_version': '1.0',
    'root': BASE_DIR,
}

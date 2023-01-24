import logging

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.pymongo import PyMongoIntegration

from .base import APP_ENV
from .env import ENV


SENTRY_ENABLED = bool(ENV.str('SENTRY_DSN', ''))
SENTRY_SAMPLING_IGNORE_PATH_LIST = ENV.list(
    var='SENTRY_SAMPLING_IGNORE_PATH_LIST',
    cast=str,
    default=['/status'],
)


def traces_sampler(context):
    try:
        if context["asgi_scope"]["path"] in SENTRY_SAMPLING_IGNORE_PATH_LIST:
            return 0
        return 1.0
    except Exception:  # skipcq: PYL-W0703
        return 1.0


if SENTRY_ENABLED:
    sentry_sdk.init(
        dsn=ENV.str('SENTRY_DSN', ''),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            PyMongoIntegration(),
            LoggingIntegration(
                # Capture info and above as breadcrumbs
                level=logging.INFO,
                # Send errors as events
                event_level=logging.ERROR,
            ),
        ],
        environment=APP_ENV,
        attach_stacktrace=True,
        request_bodies='always',
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        # traces_sample_rate=1.0,
        traces_sampler=traces_sampler,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        # ... SDK config
        _experiments={
            "profiles_sample_rate": 1.0,
        },
    )

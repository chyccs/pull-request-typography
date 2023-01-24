import os
from datetime import timedelta
from urllib.parse import urlparse

import structlog
from celery import Celery
from celery.schedules import crontab
from celery.signals import (
    task_prerun,
    worker_process_init,
    worker_process_shutdown,
)
from django.conf import settings
from django.db import connection

#
# # Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hwr_analyzer.settings')
#
app = Celery('hwr_analyzer')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_transport_options = {
    'queue_order_strategy': 'priority',
}
# # Load task modules from all registered Django apps.
app.autodiscover_tasks()
#

CELERY_TASK_TIME_LIMIT = 30 * 60

REDIS_URL = 'redis://redis:6379'
redis_url_info = urlparse(REDIS_URL)
REDIS_PASSWORD = ''
CELERY_BROKER_URL = f"{redis_url_info.scheme}://:{REDIS_PASSWORD}@{redis_url_info.netloc}"

app.conf.broker_url = 'redis://redis:6379/0'
app.conf.result_backend = 'redis://redis:6379/0'

CELERY_BROKER_USE_SSL = {}
REDIS_TLS = False

CELERY_TIMEZONE = 'Asia/Seoul'

CELERY_RESULT_BACKEND = "redis"
CELERY_RESULT_EXPIRES = timedelta(days=7)

CELERY_TASK_TRACK_STARTED = True  # c.f. https://stackoverflow.com/a/38267978

logger = structlog.getLogger()

app.conf.timezone = 'Asia/Seoul'

LOG_EVENT = 'celery-worker'
DB_CONN = None


@task_prerun.connect()
def task_pre_run(**kwargs):
    logger.info(LOG_EVENT, msg='task pre run', data=kwargs)
    global DB_CONN  # skipcq: PYL-W0602, PYL-W0603
    if not DB_CONN or not DB_CONN.is_usable:
        logger.error(LOG_EVENT, msg='mongo connection is invalid', data=connection)


@worker_process_init.connect
def init_worker(**kwargs):
    logger.info(LOG_EVENT, msg=f'initializing worker DEBUG : {settings.DEBUG}', data=kwargs)
    global DB_CONN  # skipcq: PYL-W0602, PYL-W0603
    if connection and not DB_CONN:
        DB_CONN = connection
        logger.info(LOG_EVENT, msg='initializing database connection for worker.')

    if not DB_CONN or not DB_CONN.is_usable:
        logger.error(LOG_EVENT, msg='mongo connection is invalid', data=connection)

    connection.ensure_connection()


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    logger.info(LOG_EVENT, msg='shutdown worker', data=kwargs)
    global DB_CONN  # skipcq: PYL-W0602, PYL-W0603
    if DB_CONN:
        try:
            DB_CONN.connection.client.close()
        except Exception as ex:  # skipcq: PYL-W0703
            logger.error(LOG_EVENT, msg='failed to closing database connection for worker.', err=ex)


RECOGNITION_HEALTH_CHECK_MINUTE = settings.ENV.str('RECOGNITION_HEALTH_CHECK_MINUTE', "*/30")


app.conf.beat_schedule = {
    'recognition_health_check': {
        'task': 'services.restful.tasks.try_recognize_to_health_check',
        'schedule': crontab(minute=RECOGNITION_HEALTH_CHECK_MINUTE),
    },
}

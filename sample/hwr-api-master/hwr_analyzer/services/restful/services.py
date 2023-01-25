import json

from domain.ndp.services.ndp_requester import fetch_entire_users
from services.restful.models import (
    RecognitionTasks,
    RecognitionTaskStatus,
)
from utils import logging as logger


def create_task(requester, pages):
    logger.info(msg='started', data=pages)
    task = RecognitionTasks.objects.create(
        status=RecognitionTaskStatus.PENDING,
        request=json.dumps(pages, ensure_ascii=False),
        requested_by=requester,
    )
    logger.info(msg='finished', data=task)
    return task


def has_permission_to_access_user(service_user_id: str, user_id: str):
    return user_id in fetch_entire_users(service_user_id)

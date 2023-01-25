from drf_spectacular.utils import extend_schema
from pymongo import MongoClient
from rest_framework import status
from rest_framework.permissions import AllowAny

from services.restful.views.recognizer import BaseRecognizerView
from utils.exceptions.service_unavailable import ServiceUnavailableError
from utils.response import APIResponse
from utils.validation import (
    JsonSchema,
    validate_request,
)


class HealthCheckTaskView(BaseRecognizerView):
    permission_classes = [AllowAny]

    GET_QUERY_PARAMS_SCHEMA = JsonSchema.object(
        {
            'resource': JsonSchema.array(JsonSchema.string_enum(['database']), max_items=1),
        },
        required=[],
        additional_properties=False,
    )

    @classmethod
    def _is_database_alive(cls) -> bool:
        try:
            return MongoClient().admin.command('ping').get('ok') is not None
        except Exception:  # skipcq: PYL-W0703
            return False

    @extend_schema(exclude=True)
    @validate_request(query_params_schema=GET_QUERY_PARAMS_SCHEMA)
    def get(self, request):
        data = {}
        resources = set(request.query_params.getlist('resource'))
        for resource in resources:
            if self._is_database_alive():
                data[resource] = 'UP'
            else:
                data[resource] = 'OUT_OF_SERVICE'
                raise ServiceUnavailableError(message='service is unavailable', data=data)

        return APIResponse(
            status=status.HTTP_200_OK,
            message='success',
            data=data,
        )

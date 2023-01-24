from typing import Callable

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
)


class AssertionMixin:
    '''
    Mixin for assertion helpers
    '''

    assertEqual: Callable

    def assertOK(self, response):
        self.assertEqual(response.status_code, HTTP_200_OK, response.data)

    def assertCreated(self, response):
        self.assertEqual(response.status_code, HTTP_201_CREATED, response.data)

    def assertAccepted(self, response):
        self.assertEqual(response.status_code, HTTP_202_ACCEPTED, response.data)

    def assertNoContent(self, response):
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT, response.data)

    def assertBadRequest(self, response):
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST, response.data)

    def assertUnauthorized(self, response):
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED, response.data)

    def assertForbidden(self, response):
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN, response.data)

    def assertInvalidParam(self, response):
        self.assertBadRequest(response)

    def assertNotFound(self, response):
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND, response.data)

    def assertConflict(self, response):
        self.assertEqual(response.status_code, HTTP_409_CONFLICT, response.data)

    def assertServiceUnavailableError(self, response):
        self.assertEqual(response.status_code, HTTP_503_SERVICE_UNAVAILABLE, response.data)

    def assertInternalServer(self, response):
        self.assertEqual(response.status_code, HTTP_500_INTERNAL_SERVER_ERROR, response.data)

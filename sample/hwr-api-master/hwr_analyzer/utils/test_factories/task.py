from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory
from factory.fuzzy import (
    FuzzyChoice,
    FuzzyDateTime,
)

from services.restful.models import (
    RecognitionTasks,
    RecognitionTaskStatus,
)


class RecognitionTaskFactory(DjangoModelFactory):
    class Meta:
        model = RecognitionTasks

    status = FuzzyChoice(list(RecognitionTaskStatus.choices))
    request = factory.Faker('json')
    result = factory.Faker('json')
    requested_at = FuzzyDateTime(timezone.now())
    processed_at = FuzzyDateTime(timezone.now() + timedelta(minutes=11), timezone.now() + timedelta(minutes=1000))

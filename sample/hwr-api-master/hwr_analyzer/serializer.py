import json
from abc import (
    ABC,
    abstractmethod,
)


class JsonSerializable(ABC):

    @staticmethod
    def _validate_json(data):
        json.dumps(data)

    def serialize(self, validate=False):
        data = self._serialize_to_json()
        if validate:
            self._validate_json(data)

        return data

    @abstractmethod
    def _serialize_to_json(self):
        """ Return json serializable python type. """


class JsonDeserializable(JsonSerializable):

    @classmethod
    def deserialize(cls, data: dict, validate=False):
        if validate:
            cls._validate_json(data)
        return cls._deserialize_from_json(data)

    @classmethod
    @abstractmethod
    def _deserialize_from_json(cls, data: dict):
        pass

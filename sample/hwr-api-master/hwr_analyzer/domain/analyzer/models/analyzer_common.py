from ctypes import (
    Structure,
    c_float,
)
# Define the types we need.
from enum import IntEnum


class CtypesEnum(IntEnum):
    """A ctypes-compatible IntEnum superclass."""

    @classmethod
    def from_param(cls, obj):
        return int(obj)


class DotType(CtypesEnum):
    PEN_DOWN = 0
    PEN_MOVE = 1
    PEN_UP = 2
    PEN_HOVER = 3


class BoundingBox(Structure):
    _fields_ = [('Left', c_float),
                ('Top', c_float),
                ('Width', c_float),
                ('Height', c_float)]

    def to_dict(self):
        return {f: getattr(self, f) for f, _ in self._fields_}

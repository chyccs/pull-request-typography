import base64
from ctypes import (
    POINTER,
    Structure,
    c_byte,
    c_char,
    c_double,
    c_float,
    c_int,
    c_long,
    c_short,
    memmove,
    pointer,
    sizeof,
)
from typing import List

from more_itertools import (
    first,
    last,
)

from domain.analyzer.models.analyzer_common import (
    BoundingBox,
    DotType,
)
from domain.analyzer.models.analyzer_dot import AnalyzerDot

# pylint: disable=C0103


class AnalyzerStroke(Structure):
    _fields_ = [('Id', c_int),
                ('sectionId', c_int),
                ('ownerId', c_int),
                ('noteId', c_int),
                ('pageId', c_int),
                ('WordNumber', c_int),
                ('StartTime', c_long),
                ('EndTime', c_long),
                ('DotCount', c_int),
                ('Processed', c_char),
                ('AngleRadian', c_double),
                ('ScaleBlock', c_double),
                ('PageAngleDegree', c_double),
                ('PageAngleRadian', c_double),
                ('PageRotated', c_char),
                ('Rect', BoundingBox),
                ('FontRect', BoundingBox),
                ('XAvg', c_float),
                ('YAvg', c_float),
                ('XMin', c_float),
                ('YMin', c_float),
                ('XMax', c_float),
                ('YMax', c_float),
                ('dotList', POINTER(AnalyzerDot)),
                ('length_x', c_float),
                ('length_y', c_float),
                ('length_L1', c_float),
                ('length_L2', c_float),
                ('length_L2_cumulative', c_float),
                ('radius', c_float)]

    def __str__(self):
        return f'Id: {self.Id}, sectionId: {self.sectionId}, ownerId: {self.ownerId}, noteId: {self.noteId}'

    def __init__(self, stroke_id, section_id, owner_id, note_id, page_id, *args, **kwargs):
        self.Id = stroke_id
        self.sectionId = section_id
        self.ownerId = owner_id
        self.noteId = note_id
        self.pageId = page_id

    def initialize(self, startTime, dots, *args, **kwargs):
        dots_bytes = base64.b64decode(dots)
        if len(dots_bytes) % 17 != 0:
            raise ValueError(f'total dot length is {len(dots_bytes)} bytes. single dot must be 17 bytes long.')

        dot_count = int(len(dots_bytes) / 17)
        bdots = (dot_count * BinaryDot)()
        memmove(pointer(bdots), dots_bytes, sizeof(bdots))
        base_time = startTime
        analyzer_dots = [AnalyzerDot(**item.to_dict()) for item in bdots if item.is_valid()]

        for index, item in enumerate(analyzer_dots):
            item.StrokeId = self.Id
            item.Timestamp = base_time + item.Timestamp
            base_time = item.Timestamp
            item.dotType = DotType.PEN_MOVE
            item.Count = index

        first(analyzer_dots).dotType = DotType.PEN_DOWN
        last(analyzer_dots).dotType = DotType.PEN_UP

        c_dots_array = (len(analyzer_dots) * AnalyzerDot)()
        for index, item in enumerate(analyzer_dots):
            c_dots_array[index] = item

        self.StartTime = startTime  # skipcq: PYL-W0201
        self.EndTime = base_time  # skipcq: PYL-W0201
        self.DotCount = dot_count  # skipcq: PYL-W0201
        self.dotList = c_dots_array  # skipcq: PYL-W0201

    def from_analyzer_dots(self, analyzer_dots: List[AnalyzerDot]):
        first(analyzer_dots).dotType = DotType.PEN_DOWN
        last(analyzer_dots).dotType = DotType.PEN_UP

        c_dots_array = (len(analyzer_dots) * AnalyzerDot)()
        for index, item in enumerate(analyzer_dots):
            item.StrokeId = self.Id
            c_dots_array[index] = item

        self.StartTime = first(analyzer_dots).Timestamp  # skipcq: PYL-W0201
        self.EndTime = last(analyzer_dots).Timestamp  # skipcq: PYL-W0201
        self.DotCount = len(analyzer_dots)  # skipcq: PYL-W0201
        self.dotList = c_dots_array  # skipcq: PYL-W0201


class BinaryDot(Structure):
    _pack_ = 1
    _fields_ = [('timestamp', c_short),
                ('force', c_float),
                ('x', c_float),
                ('y', c_float),
                ('tx', c_byte),
                ('ty', c_byte),
                ('rotation', c_byte)]

    def __str__(self):
        return f'x: {self.x}, y: {self.y}, force: {self.force}, ts: {self.timestamp}'

    def to_dict(self):
        return {'x': self.x, 'y': self.y, 'force': self.force, 'timestamp': self.timestamp}

    def is_valid(self):
        for field in self._fields_:
            title = field[0].lower()
            value = (getattr(self, title) & 0xff) if field[1] == c_byte else getattr(self, title)
            if title != 'timestamp' and value < 0:
                raise ValueError(f'{title} must larger than 0')

        return True


def create_analyzer_stroke_array(analyze_strokes: List[AnalyzerStroke]):
    c_stroke_array = (len(analyze_strokes) * AnalyzerStroke)()
    for index, item in enumerate(analyze_strokes):
        c_stroke_array[index] = item

    return c_stroke_array

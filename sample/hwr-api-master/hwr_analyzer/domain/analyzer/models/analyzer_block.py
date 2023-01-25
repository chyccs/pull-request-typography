from ctypes import (
    POINTER,
    Structure,
    c_bool,
    c_double,
    c_float,
    c_int,
    c_long,
)

from domain.analyzer.models.analyzer_common import BoundingBox
from domain.analyzer.models.analyzer_stroke import AnalyzerStroke


class AnalyzerBlock(Structure):
    _fields_ = [('sectionId', c_int),
                ('ownerId', c_int),
                ('noteId', c_int),
                ('pageId', c_int),
                ('Id', c_int),
                ('Processed', c_bool),
                ('StartTime', c_long),
                ('EndTime', c_long),
                ('Rect', BoundingBox),
                ('FontRect', BoundingBox),
                ('TransformedRect', BoundingBox),
                ('TransformedFontRect', BoundingBox),
                ('blockgroupRect', BoundingBox),
                ('AngleDegree', c_double),
                ('AngleRadian', c_double),
                ('PageAngleDegree', c_double),
                ('PageAngleRadian', c_double),
                ('RotateCenterPointX', c_float),
                ('RotateCenterPointY', c_float),
                ('StrokeIdxStart', c_int),
                ('StrokeIdxEnd', c_int),
                ('StrokeCount', c_int),
                ('groupNumber', c_int),
                ('ShapePossibility', c_bool),
                ('BlockTypeMemo', c_bool),
                ('block_slope', c_double),
                ('block_intercept', c_float),
                ('strokeList', POINTER(AnalyzerStroke))]

    def __str__(self):
        return f's:{self.sectionId}, o:{self.ownerId}, b:{self.noteId}, p:{self.pageId}, strokes:{self.StrokeCount}'

from ctypes import (
    Structure,
    c_bool,
    c_double,
    c_float,
    c_int,
    c_long,
)

from domain.analyzer.models.analyzer_common import BoundingBox


class AnalyzerBlockResponse(Structure):
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
                ('block_intercept', c_float)]

    def __str__(self):
        return f's:{self.sectionId}, o:{self.ownerId}, b:{self.noteId}, p:{self.pageId}, strokes:{self.StrokeCount}'

    def to_dict(self):
        def convert(attr):
            if hasattr(attr, 'to_dict'):
                return attr.to_dict()
            return attr
        return {f: convert(getattr(self, f)) for f, _ in self._fields_}

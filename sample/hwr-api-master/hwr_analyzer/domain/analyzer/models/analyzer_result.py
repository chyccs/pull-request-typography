import itertools
from ctypes import (
    POINTER,
    Structure,
    c_int,
    cast,
)
from itertools import groupby
from typing import (
    Dict,
    List,
)

from domain.analyzer.models.analyzer_block_response import AnalyzerBlockResponse
from domain.analyzer.models.analyzer_dot import AnalyzerDot
from domain.analyzer.models.analyzer_dot_response import AnalyzerDotResponse
from domain.analyzer.models.analyzer_stroke import AnalyzerStroke


class AnalyzerTemp(Structure):
    pass


class AnalyzerResult(Structure):
    _fields_ = [('count', c_int),
                ('analyzerDots', POINTER(AnalyzerTemp)),
                ('blockCount', c_int),
                ('analyzerBlocks', POINTER(AnalyzerTemp))]

    def __str__(self):
        return f'count: {self.count} / blockCount: {self.blockCount}'

    @property
    def dots(self):
        if not getattr(self, "_dots", None):
            setattr(self, "_dots", cast(self.analyzerDots, POINTER(AnalyzerDotResponse * self.count)).contents)
        return self._dots

    def to_blocks(self) -> List[Dict]:
        dots = self.dots
        grouped_data = itertools.groupby(dots, lambda x: x.BlockId)
        result = {}
        for k, v in grouped_data:
            result[k] = {dot.StrokeId for dot in v}
        block_dicts = []
        blocks = cast(self.analyzerBlocks, POINTER(AnalyzerBlockResponse * self.blockCount)).contents
        for block in blocks:
            block_dict = block.to_dict()
            block_dict['StrokeIds'] = sorted(result[block.Id])
            block_dicts.append(block_dict)
        return block_dicts

    def to_recognize_strokes(self, scale: int = 1) -> List[Dict]:
        dots = self.dots
        strokes = groupby(dots, lambda x: x.StrokeId)

        def build_stroke(key, items):
            xs, ys, ts, ps = [], [], [], []
            for item in items:
                xs.append(item.X * scale)
                ys.append(item.Y * scale)
                ts.append(item.Timestamp)
                ps.append(key)

            return {
                "id": key,
                "x": xs,
                "y": ys,
                "t": ts,
                "p": ps,
                "pointerType": "PEN",
                "pointerId": 0,
            }

        return [build_stroke(key, items) for key, items in strokes]

    def to_analyzer_strokes(self, section_id, owner_id, note_id, page_id):
        dots = self.dots
        raw_strokes = groupby(dots, lambda x: x.StrokeId)

        def build_stroke(stroke_id, dots):
            analyzer_stroke = AnalyzerStroke(stroke_id=stroke_id,
                                             section_id=section_id,
                                             owner_id=owner_id,
                                             note_id=note_id,
                                             page_id=page_id)
            analyzer_stroke.from_analyzer_dots([AnalyzerDot(d.X, d.Y, d.Force / 2047, d.Timestamp) for d in dots])
            return analyzer_stroke

        analyzer_strokes = [build_stroke(stroke_id, dots) for stroke_id, dots in raw_strokes]
        c_stroke_array = (len(analyzer_strokes) * AnalyzerStroke)()
        for index, item in enumerate(analyzer_strokes):
            c_stroke_array[index] = item
        return c_stroke_array

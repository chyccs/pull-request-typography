import ctypes
from ctypes import cdll

from domain.analyzer.models.analyzer_result import AnalyzerResult
from domain.analyzer.models.analyzer_stroke import AnalyzerStroke
from hwr_analyzer import settings

G_JIIX_STR_DATA_IDX = 0

# 현재 페이지의 Word block 각도값이 단일 각도 범위로 수렴하지 않는다. (메모형 페이지 가능성 있음)
G_MEMOTYPE_PAGE = 0

# 현재 페이지의 회전각 추정치. Radian
G_FOUND_PAGE_ANGLE_RAD = 0.0

# 현재 페이지의 회전각 추정치. Degree
G_FOUND_PAGE_ANGLE_DEG = 0.0


class StrokeAnalyzer:
    def __init__(self):
        super().__init__()

        self.clib = cdll.LoadLibrary(settings.ANALYZER_LIB_PATH)

        self.set_paper_max_width = self.clib.SetPaperMaxWidth
        self.set_paper_max_width.argtypes = (ctypes.c_float,)
        self.set_paper_max_width.restype = ctypes.c_float

        self.set_paper_max_height = self.clib.SetPaperMaxHeight
        self.set_paper_max_height.argtypes = (ctypes.c_float,)
        self.set_paper_max_height.restype = ctypes.c_float

        self.init = self.clib.Init
        self.init.argtypes = (ctypes.c_float, ctypes.c_float, ctypes.c_int, ctypes.c_int)
        self.init.restype = ctypes.c_bool

        self.finalize = self.clib.Finalize

        self.do_stroke_analyze_to_block = self.clib.do_stroke_analyze_to_block

    def get_version(self):
        return self.get_version()  # pragma: no cover

    def set_paper_size(self, width_mm, height_mm):
        self.set_paper_max_width(width_mm)  # pragma: no cover
        self.set_paper_max_height(height_mm)  # pragma: no cover

    def initialize(self,
                   page_width_mm=210,
                   page_height_mm=297,
                   block_size_sampling_steps=3,
                   kind_of_engine=0):
        return self.init(page_width_mm, page_height_mm, block_size_sampling_steps, kind_of_engine)

    def dispose(self, release_all: bool):
        self.finalize(release_all)

    # 2차 전처리
    def run(self, original_strokes, page_radian, count):
        if count <= 0:
            return None

        self.do_stroke_analyze_to_block.argtypes = [
            ctypes.POINTER(AnalyzerStroke * count),
            ctypes.c_int,
            ctypes.c_double,
            ctypes.c_bool,
        ]
        self.do_stroke_analyze_to_block.restype = ctypes.POINTER(AnalyzerResult)

        processed_block = self.do_stroke_analyze_to_block(
            original_strokes,
            count,
            page_radian,
            False)
        return processed_block

    # 1차 전처리
    def angle_elimination(self, original_strokes, count):
        self.do_stroke_analyze_to_block.argtypes = [
            ctypes.POINTER(AnalyzerStroke * count),
            ctypes.c_int,
            ctypes.c_double,
            ctypes.c_bool,
        ]
        self.do_stroke_analyze_to_block.restype = ctypes.POINTER(AnalyzerResult)
        processed_block = self.do_stroke_analyze_to_block(
            original_strokes,
            count,
            G_FOUND_PAGE_ANGLE_RAD,
            True,
        )
        return processed_block

    def __enter__(self):
        return StrokeAnalyzer()  # pragma: no cover

    def __exit__(self, type, value, traceback):  # skipcq: PYL-W0622
        self.finalize()  # pragma: no cover

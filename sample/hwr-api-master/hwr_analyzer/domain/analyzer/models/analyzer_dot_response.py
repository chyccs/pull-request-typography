from ctypes import (
    Structure,
    c_float,
    c_int,
    c_long,
)


class AnalyzerDotResponse(Structure):
    _fields_ = [('BlockId', c_int),
                ('StrokeId', c_int),
                ('dotType', c_int),
                ('X', c_float),
                ('Y', c_float),
                ('Force', c_int),
                ('Timestamp', c_long)]

    def __str__(self):
        return f'block:{self.BlockId},stroke:{self.StrokeId},x:{self.X},y:{self.Y},f:{self.Force},ts:{self.Timestamp}'

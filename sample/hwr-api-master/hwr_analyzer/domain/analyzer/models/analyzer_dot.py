from ctypes import (
    Structure,
    c_float,
    c_int,
    c_long,
)


class AnalyzerDot(Structure):
    _fields_ = [('StrokeId', c_int),
                ('dotType', c_int),
                ('X', c_float),
                ('Y', c_float),
                ('tiltX', c_int),
                ('tiltY', c_int),
                ('Force', c_int),
                ('Twist', c_int),
                ('Timestamp', c_long),
                ('Count', c_int)]

    def __init__(self, x, y, force, timestamp, *args, **kwargs):
        self.X = x
        self.Y = y
        self.Force = int(force * 2047)
        self.Timestamp = abs(timestamp)

    def __str__(self):
        return f'Id: {self.StrokeId}, x: {self.X}, y: {self.Y}, f: {self.Force}, ts: {self.Timestamp}'

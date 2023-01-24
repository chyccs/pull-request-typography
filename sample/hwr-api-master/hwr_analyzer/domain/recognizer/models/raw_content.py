from typing import (
    Dict,
    List,
)


class BoundingBox:
    x: float
    y: float
    width: float
    height: float

    def __init__(self, x: float, y: float, width: float, height: float, *args, **kwargs):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return f'{self.x}, {self.y}, {self.width}, {self.height}'


class Stroke:
    id: int

    def __init__(self, f: List[int], *args, **kwargs):
        self.id = f[0]

    def __str__(self):
        return f'{self.id}'


class RawContentItem:
    type: str
    content: Dict

    def __init__(self, content):
        self.type = content['type']
        self.content = content

    def __str__(self):
        return f'{self.type}'


class RawContentContainer:
    type: str
    elements: List[RawContentItem]

    def __init__(self, type: str, elements, *args, **kwargs):  # skipcq: PYL-W0622
        self.type = type
        self.elements = [RawContentItem(element) for element in elements]

    def __str__(self):
        return f'{self.type}, {self.elements}'

    @property
    def text_stroke_ids(self):
        if not getattr(self, "_text_stroke_ids", None):
            ids = []
            for element in self.elements:
                if element.type == 'Text' and element.content.get('words'):
                    for word in element.content.get('words'):
                        if not word.get('items'):
                            continue
                        for item in word.get('items'):
                            ids.append(item.get('F')[0])
            setattr(self, "_text_stroke_ids", ids)
        return self._text_stroke_ids

    @property
    def non_text_stroke_ids(self):
        if not getattr(self, "_non_text_stroke_ids", None):
            ids = []
            for element in self.elements:
                if element.type in ['Edge', 'Node'] and element.content.get('items'):
                    for item in element.content.get('items'):
                        ids.append(item.get('F')[0])
            setattr(self, "_non_text_stroke_ids", ids)
        return self._non_text_stroke_ids

    def is_text_stroke(self, stroke_id):
        return stroke_id not in self.non_text_stroke_ids

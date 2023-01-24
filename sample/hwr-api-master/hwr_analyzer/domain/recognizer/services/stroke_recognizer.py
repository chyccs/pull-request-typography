import binascii
import json
from ctypes import byref
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Any,
    Dict,
    List,
)

import jsons
import requests
from bson.objectid import ObjectId
from django.utils import timezone

from domain.analyzer.models.analyzer_stroke import (
    AnalyzerStroke,
    create_analyzer_stroke_array,
)
from domain.analyzer.services.stroke_analyzer import StrokeAnalyzer
from domain.recognizer.models.raw_content import RawContentContainer
from domain.recognizer.services.iink_requester import (
    SerializedStroke,
    recognize,
)
from hwr_analyzer.celery import app
from hwr_analyzer.settings import (
    ANALYZER_BLOCK_SIZE_SAMPLING_STEPS,
    ANALYZER_KIND_OF_ENGINE,
    ANALYZER_PAPER_HEIGHT,
    ANALYZER_PAPER_WIDTH,
    IINK_HEIGHT,
    IINK_SCALE,
    IINK_WIDTH,
    IINK_XDPI,
    IINK_YDPI,
)
from services.restful.models import (
    RecognitionTasks,
    RecognitionTaskStatus,
    RecognizedDocument,
)
from utils import logging as logger


@dataclass(frozen=True)
class Recognition:

    @dataclass(frozen=True)
    class Analyzer:
        paper_width: int = ANALYZER_PAPER_WIDTH
        paper_height: int = ANALYZER_PAPER_HEIGHT
        block_size_sampling_steps: int = ANALYZER_BLOCK_SIZE_SAMPLING_STEPS
        kind_of_engine: int = ANALYZER_KIND_OF_ENGINE
        separate_shapes_and_text: bool = True
        hide: bool = False
        remove_shape: bool = True

    content_type: str
    language: str
    width: int = IINK_WIDTH
    height: int = IINK_HEIGHT
    x_dpi: int = IINK_XDPI
    y_dpi: int = IINK_YDPI
    scale: int = IINK_SCALE
    analyzer: Analyzer = Analyzer()
    configuration: Dict[str, Any] = field(default_factory=Dict[str, Any])

    def __post_init__(self):
        self.configuration['lang'] = self.language


def _make_analyzer_strokes(page) -> List[AnalyzerStroke]:
    def _to_analyzer_stroke(index, page, contents) -> AnalyzerStroke:
        analyzer_stroke = AnalyzerStroke(index, page['section'], page['owner'], page['bookCode'], page['pageNumber'])
        analyzer_stroke.initialize(**contents)
        return analyzer_stroke

    return [
        _to_analyzer_stroke(index, page, item)
        for index, item in enumerate(page['strokes']) if item['deleteFlag'] == 0
    ]


def _create_recognized_document(user_id: str, result: Dict, page: Dict):
    def pick_candidate(candidates):
        return [{'rank': i, 'label': v} for i, v in enumerate(candidates)]

    return RecognizedDocument(
        section_code=page['section'],
        owner_code=page['owner'],
        note_code=page['bookCode'],
        note_uuid=page['noteUUID'],
        page_number=page['pageNumber'],
        user_id=user_id,
        language=page['recognition']['language'],
        label=result['iink'].get('label'),
        words=[{
            'label': word.get('label'),
            'candidates': pick_candidate(word.get('candidates')) if word.get('candidates') else None,
        } for word in result['iink'].get('words') if word['label'].strip()] if result['iink'].get('words') else None,
    )


def update_recognition_task(task, result, pages):
    need_to_save = zip(result, pages)
    save_items = [
        _create_recognized_document(
            user_id=task.requested_by,
            result=result,
            page=page,
        ) for result, page in need_to_save
    ]

    for item in save_items:
        logger.info(msg="recognized text", data=item)
        item.save()

    task.status = RecognitionTaskStatus.DONE
    task.processed_at = timezone.now()
    task.result = json.dumps(result, ensure_ascii=False)
    task.save()


@app.task
def recognize_pages_async(task_id: str):
    logger.info(msg="recognize_pages_async")
    try:
        task = RecognitionTasks.objects.get(pk=ObjectId(task_id))
        logger.info(msg="task fetched", data=task)
        pages = json.loads(task.request)
        result = [recognize_page(page) for page in pages]
        update_recognition_task(task, result, pages)
        return task.result

    except RecognitionTasks.DoesNotExist as ex:
        logger.error(msg="task is not found", err=ex)
        raise

    except (requests.RequestException, requests.HTTPError) as ex:  # skipcq: PYL-W0714
        logger.error(msg="iink server request error", err=ex)
        raise

    except binascii.Error as err:
        logger.error(msg="data parsing error", err=err)
        raise

    except Exception as ex:  # skipcq: PYL-W0703
        logger.error(msg="unknown error", err=ex)
        raise


def _filter_shape(
    need_raw_recognize: List[SerializedStroke],
    need_analyze: List[AnalyzerStroke],
    config: Recognition,
) -> RawContentContainer:
    config_for_separate = config.configuration.copy()
    config_for_separate['raw-content'] = {'recognition': {'shape': True, 'text': True}}

    raw_content_res = recognize(
        width=config.width,
        height=config.height,
        x_dpi=config.x_dpi,
        y_dpi=config.y_dpi,
        strokes=need_raw_recognize,
        content_type="Raw Content",
        iink_config=config_for_separate,
    )

    raw_content = RawContentContainer(**raw_content_res.json())

    if config.analyzer.remove_shape:
        filtered = [item for item in need_analyze if raw_content.is_text_stroke(item.Id)]
        need_analyze = create_analyzer_stroke_array(filtered)
        logger.info(msg='shape is removed')

    return raw_content


def _build_response(analyzer_result, recognizer_result, raw_content, config: Recognition):
    response_of_analyzer = {'analyzerBlocks': analyzer_result.contents.to_blocks()}
    if raw_content and config.analyzer.separate_shapes_and_text:
        response_of_analyzer['processedText'] = raw_content.text_stroke_ids
        response_of_analyzer['processedShape'] = raw_content.non_text_stroke_ids

    response = {
        'analyzer': response_of_analyzer,
        'iink': recognizer_result.json(),
    }

    if config.analyzer.hide:
        response.pop('analyzer')

    logger.info(msg='done')
    return response


def recognize_page(page: Dict):
    logger.info(msg='begin', data=page)
    config = jsons.load(page['recognition'], cls=Recognition, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE)

    stroke_array = create_analyzer_stroke_array(_make_analyzer_strokes(page))

    stroke_analyzer = StrokeAnalyzer()
    stroke_analyzer.initialize(
        page_width_mm=config.analyzer.paper_width,
        page_height_mm=config.analyzer.paper_height,
        block_size_sampling_steps=config.analyzer.block_size_sampling_steps,
        kind_of_engine=config.analyzer.kind_of_engine,
    )

    elim_result = stroke_analyzer.angle_elimination(original_strokes=byref(stroke_array), count=len(stroke_array))
    logger.info(msg='angle_elimination', data=elim_result)

    strokes_to_analyze = elim_result.contents.to_analyzer_strokes(
        section_id=page['section'],
        owner_id=page['owner'],
        note_id=page['bookCode'],
        page_id=page['pageNumber'],
    )
    strokes_to_raw_recognize = elim_result.contents.to_recognize_strokes(scale=config.scale)
    page_radian = elim_result.contents.to_blocks()[0]['PageAngleRadian']
    stroke_analyzer.dispose(False)

    raw_content = None
    if config.analyzer.remove_shape or config.analyzer.separate_shapes_and_text:
        try:
            raw_content = _filter_shape(
                need_raw_recognize=strokes_to_raw_recognize,
                need_analyze=strokes_to_analyze,
                config=config,
            )
        except (requests.RequestException, requests.HTTPError):  # skipcq: PYL-W0714
            stroke_analyzer.dispose(True)
            raise

    analyzer_result = stroke_analyzer.run(
        original_strokes=byref(strokes_to_analyze),
        page_radian=page_radian,
        count=len(strokes_to_analyze),
    )
    logger.info(msg='stroke_analyzer.run')

    stroke_to_recognize = analyzer_result.contents.to_recognize_strokes(scale=config.scale)
    stroke_analyzer.dispose(True)

    recognizer_result = recognize(
        width=config.width,
        height=config.height,
        x_dpi=config.x_dpi,
        y_dpi=config.y_dpi,
        strokes=stroke_to_recognize,
        content_type=config.content_type,
        iink_config=config.configuration,
    )
    logger.info(msg='recognized', data=recognizer_result)

    return _build_response(
        analyzer_result=analyzer_result,
        recognizer_result=recognizer_result,
        raw_content=raw_content,
        config=config,
    )

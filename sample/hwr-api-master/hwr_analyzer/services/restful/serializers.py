from rest_framework import serializers

from hwr_analyzer.settings import (
    ANALYZER_BLOCK_SIZE_SAMPLING_STEPS,
    ANALYZER_KIND_OF_ENGINE,
    ANALYZER_PAPER_HEIGHT,
    ANALYZER_PAPER_WIDTH,
    HWR_API_VALID_CONTENT_TYPE_LIST,
    IINK_HEIGHT,
    IINK_SCALE,
    IINK_WIDTH,
    IINK_XDPI,
    IINK_YDPI,
)


class CommonSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass  # for fixing abstract method not overridden issue

    def create(self, validated_data):
        pass  # for fixing abstract method not overridden issue


class AnalyzerSerializer(CommonSerializer):
    remove_shape = serializers.BooleanField(help_text="도형 제거", required=False, default=True)
    separate_shapes_and_text = serializers.BooleanField(help_text="스트로크 인덱스를 도형과 문자로 분류", required=False, default=True)
    paper_width = serializers.IntegerField(help_text="종이 너비", required=False, default=ANALYZER_PAPER_WIDTH)
    paper_height = serializers.IntegerField(help_text="종이 높이", required=False, default=ANALYZER_PAPER_HEIGHT)
    block_size_sampling_steps = serializers.IntegerField(help_text="블럭 사이즈 샘플링 단위",
                                                         required=False,
                                                         default=ANALYZER_BLOCK_SIZE_SAMPLING_STEPS)
    kind_of_engine = serializers.IntegerField(help_text="엔진 타입", required=False, default=ANALYZER_KIND_OF_ENGINE)


class RecognitionSerializer(CommonSerializer):
    x_dpi = serializers.IntegerField(help_text="X Dpi", required=False, default=IINK_XDPI)
    y_dpi = serializers.IntegerField(help_text="Y Dpi", required=False, default=IINK_YDPI)
    width = serializers.IntegerField(help_text="너비", required=False, default=IINK_WIDTH)
    height = serializers.IntegerField(help_text="높이", required=False, default=IINK_HEIGHT)
    scale = serializers.IntegerField(help_text="좌표 스케일", required=False, default=IINK_SCALE)
    language = serializers.CharField(help_text="인식 언어", required=True)
    content_type = serializers.ChoiceField(help_text="인식 타입",
                                           required=True,
                                           choices=('Text', 'Diagram', 'Raw Content', 'Math'))
    configuration = serializers.JSONField(help_text="iink 추가 설정", required=False)
    analyzer = AnalyzerSerializer(help_text="애널라이저 설정", required=False)


class StrokeSerializer(CommonSerializer):
    delete_flag = serializers.BooleanField(help_text="삭제 여부", required=True)
    start_time = serializers.IntegerField(help_text="스트로크 시작 시간", required=True)
    dot_count = serializers.IntegerField(help_text="총 도트수", required=True)
    dots = serializers.CharField(help_text="도트(base64 인코딩)", required=True)


class PageSerializer(CommonSerializer):
    noteUUID = serializers.UUIDField(help_text="노트 UUID (페이지 번호와 함께 사용)", label='noteUUID', required=True)
    page_number = serializers.IntegerField(help_text="페이지 번호", required=True)
    pageUUID = serializers.UUIDField(help_text="페이지 UUID (노트 UUID 없이 단독으로 사용)", label='pageUUID', required=True)
    query_type = serializers.ChoiceField(help_text="Stroke 필터링 기준",
                                         required=True,
                                         choices=('SNAPSHOT', 'CONTAIN_DELETED'))
    recognition = RecognitionSerializer(help_text="필기 인식 관련 Configuration", required=True)


class PageWithStrokesSerializer(CommonSerializer):
    section = serializers.IntegerField(help_text="섹션 코드", required=True)
    owner = serializers.IntegerField(help_text="오너 코드", required=True)
    book_code = serializers.IntegerField(help_text="북코드", required=True)
    page_number = serializers.IntegerField(help_text="페이지 번호", required=True)
    recognition = RecognitionSerializer(help_text="필기 인식 관련 Configuration", required=True)
    strokes = StrokeSerializer(help_text="스트로크 리스트", many=True, required=True)


class BasePagesSerializer(CommonSerializer):
    mime_type = serializers.ChoiceField(help_text="문서 타입",
                                        required=True,
                                        choices=HWR_API_VALID_CONTENT_TYPE_LIST)


class PagesSerializer(BasePagesSerializer):
    pages = PageSerializer(help_text="페이지 리스트", many=True, required=True)


class PagesWithStrokesSerializer(BasePagesSerializer):
    pages = PageWithStrokesSerializer(help_text="페이지 리스트", many=True, required=True)


class CommonResultSerializer(CommonSerializer):
    result = serializers.ChoiceField(help_text="처리 결과", required=True, choices=('success', 'error'))
    message = serializers.CharField(help_text="내용", required=True)


class CandidateSerializer(CommonSerializer):
    rank = serializers.IntegerField(help_text="순위", required=False)
    label = serializers.CharField(help_text="필기 인식 단어 후보")


class RecognizedWordSerializer(CommonSerializer):
    label = serializers.CharField(help_text="필기 인식 단어")
    candidates = CandidateSerializer(help_text="필기 인식 단어 후보군", many=True, required=False)


class RecognizedDocumentSerializer(CommonSerializer):
    section_code = serializers.IntegerField(help_text="섹션 코드", required=True)
    owner_code = serializers.IntegerField(help_text="오너 코드", required=True)
    note_code = serializers.IntegerField(help_text="북코드", required=True)
    noteUUID = serializers.UUIDField(help_text="노트 UUID (페이지 번호와 함께 사용)", label='noteUUID', required=True)
    page_number = serializers.IntegerField(help_text="페이지 번호", required=True)
    pageUUID = serializers.UUIDField(help_text="페이지 UUID (노트 UUID 없이 단독으로 사용)", label='pageUUID', required=True)
    user_id = serializers.IntegerField(help_text="소유자", required=True)
    language = serializers.CharField(help_text="필기 인식 언어")
    label = serializers.CharField(help_text="필기 인식 결과")
    words = RecognizedWordSerializer(help_text="페이지 리스트", many=True, required=False)


class RecognitionResultSerializer(CommonSerializer):
    task_id = serializers.CharField(help_text="접수된 작업 아이디", required=True)
    result = serializers.ChoiceField(help_text="처리 결과", required=True, choices=('success', 'error'))
    message = serializers.CharField(help_text="내용", required=False)
    content = serializers.JSONField(
        help_text="필기 인식 결과 JIIX 포맷 (https://developer.myscript.com/docs/interactive-ink/2.0/reference/web/jiix/)",
        required=False,
    )


class RecognitionTaskSerializer(CommonSerializer):
    task_id = serializers.CharField(help_text="작업 아이디", required=True)
    status = serializers.ChoiceField(help_text="상태", required=True, choices=('PENDING', 'DONE', 'FAILED'))
    request = serializers.JSONField(help_text="요청", required=True)
    result = serializers.JSONField(
        help_text="필기 인식 결과 JIIX 포맷 (https://developer.myscript.com/docs/interactive-ink/2.0/reference/web/jiix/)",
        required=False,
    )
    requested_at = serializers.DateTimeField(help_text="요청 일시", required=True)
    processed_at = serializers.DateTimeField(help_text="처리 일시", required=False)

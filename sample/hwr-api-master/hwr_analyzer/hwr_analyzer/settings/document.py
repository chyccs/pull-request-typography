from hwr_analyzer import settings
from hwr_analyzer.settings import DEBUG

SPECTACULAR_SERVER_URL = 'http://0.0.0.0:8000/' if DEBUG else 'https://hwr.neolab.net/'

SPECTACULAR_SETTINGS = {
    # General schema metadata. Refer to spec for valid inputs
    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md#openapi-object
    'TITLE': 'NDP Natural Handwriting Recognition API',
    # 'DESCRIPTION': 'drf-specatular 를 사용해서 만든 API 문서입니다.',
    'SERVERS': [{'url': SPECTACULAR_SERVER_URL}],
    # Optional: MAY contain "name", "url", "email"
    'CONTACT': {
        'name': 'NeoLAB Convergence Inc.',
        'url': 'https://hwr.neolab.net',
        'email': 'support@neolab.net',
    },
    'SWAGGER_UI_SETTINGS': {
        # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/  <- 여기 들어가면 어떤 옵션들이 더 있는지 알수있습니다.
        'dom_id': '#swagger-ui',  # required(default)
        'layout': 'BaseLayout',  # required(default)
        'deepLinking': True,  # API를 클릭할때 마다 SwaggerUI의 url이 변경됩니다. (특정 API url 공유시 유용하기때문에 True설정을 사용합니다)
        'persistAuthorization': True,  # True 이면 SwaggerUI상 Authorize에 입력된 정보가 새로고침을 하더라도 초기화되지 않습니다.
        'displayOperationId': True,  # True이면 API의 urlId 값을 노출합니다. 대체로 DRF api name둘과 일치하기때문에 api를 찾을때 유용합니다.
        'filter': True,  # True 이면 Swagger UI에서 'Filter by Tag' 검색이 가능합니다
    },
    # available SwaggerUI versions: https://github.com/swagger-api/swagger-ui/releases
    "SWAGGER_UI_FAVICON_HREF": f"/{settings.STATIC_URL}favicon/cropped-icon-Ncode_05-1-32x32.png",
    # Optional: MUST contain "name", MAY contain URL
    'LICENSE': {
        'name': 'MIT License',
        'url': 'https://github.com/KimSoungRyoul/DjangoBackendProgramming/blob/main/LICENSE',
    },
    'VERSION': 'v1',
    'SERVE_INCLUDE_SCHEMA': False,  # OAS3 Meta정보 API를 비노출 처리합니다.
    'REDOC_UI_SETTINGS': {},
    # https://www.npmjs.com/package/swagger-ui-dist 해당 링크에서 최신버전을 확인후 취향에 따라 version을 수정해서 사용하세요.
    'SWAGGER_UI_DIST': '//unpkg.com/swagger-ui-dist@3.38.0',  # Swagger UI 버전을 조절할수 있습니다.
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
        'drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields',
    ],
    'CAMELIZE_NAMES': False,
    'SERVE_AUTHENTICATION': None,
}

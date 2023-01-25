from utils.validation import JsonSchema

RECOGNITION_SCHEME = JsonSchema.object({
    "xDPI": JsonSchema.number(),
    "yDPI": JsonSchema.number(),
    "width": JsonSchema.number(),
    "height": JsonSchema.number(),
    "scale": JsonSchema.number(),
    'language': JsonSchema.string(1, 50),
    'contentType': JsonSchema.string(1, 50),
    'configuration': JsonSchema.object({}),
    'analyzer': JsonSchema.object({
        "removeShape": JsonSchema.boolean(),
        "separateShapesAndText": JsonSchema.boolean(),
        "paperWidth": JsonSchema.number(),
        "paperHeight": JsonSchema.number(),
        "blockSizeSamplingSteps": JsonSchema.number(),
        "kindOfEngine": JsonSchema.number()},
        additional_properties=True,
    )},
    required=['language', 'contentType'],
    additional_properties=True,
)

STROKE_RECOGNIZE_SCHEME = JsonSchema.object({
    'mimeType': JsonSchema.string(1, 50),
    'pages': JsonSchema.array(
        JsonSchema.object({
            'noteUUID': JsonSchema.string(),
            'pageUUID': JsonSchema.string(),
            'section': JsonSchema.number(),
            'owner': JsonSchema.number(),
            'bookCode': JsonSchema.number(),
            'pageNumber': JsonSchema.number(),
            'recognition': RECOGNITION_SCHEME,
            'strokes': JsonSchema.array(
                JsonSchema.object({
                    "deleteFlag": JsonSchema.integer(),
                    "startTime": JsonSchema.number(),
                    "dotCount": JsonSchema.integer(),
                    "dots": JsonSchema.string()},
                    required=['deleteFlag', 'startTime', 'dotCount', 'dots'],
                    additional_properties=True,
                ),
            )},
            required=['section', 'owner', 'bookCode', 'pageNumber', 'recognition', 'strokes'],
            additional_properties=True,
        ),
    ),
}, required=['mimeType', 'pages'])

PAGE_RECOGNIZE_SCHEME = JsonSchema.object({
    'mimeType': JsonSchema.string(1, 50),
    'pages': JsonSchema.array(
        JsonSchema.anyOf(
            JsonSchema.object({
                'noteUUID': JsonSchema.uuid(),
                'pageNumber': JsonSchema.number(),
                'queryType': JsonSchema.string(),
                'recognition': RECOGNITION_SCHEME},
                required=['noteUUID', 'pageNumber', 'recognition'],
                additional_properties=False,
            ),
            JsonSchema.object({
                'pageUUID': JsonSchema.uuid(),
                'queryType': JsonSchema.string(),
                'recognition': RECOGNITION_SCHEME},
                required=['pageUUID', 'recognition'],
                additional_properties=False,
            ),
        ),
    ),
}, required=['mimeType', 'pages'])

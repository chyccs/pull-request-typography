import uuid
from enum import Enum
from unittest import TestCase

import stringcase
from jsonschema import (
    FormatChecker,
    ValidationError,
    validate,
)

from utils.authentications.credentials import CredentialsType
from utils.validation import (
    RRN_REGEX,
    JsonSchema,
)


class TestUuidSchema(TestCase):
    def setUp(self) -> None:
        self.data = str(uuid.uuid4())
        self.schema = JsonSchema.uuid()

    def test_uuid(self):
        validate(self.data, self.schema, format_checker=FormatChecker())

    def test_exceed_uuid_length(self):
        with self.assertRaises(ValidationError):
            validate(self.data + 'a', self.schema, format_checker=FormatChecker())


class TestRrnSchema(TestCase):
    def setUp(self) -> None:
        self.data = '000101-1234567'
        self.schema = {
            'type': 'string',
            'pattern': RRN_REGEX,
        }

    def test_rrn(self):
        validate(self.data, self.schema, format_checker=FormatChecker())

    def test_exceed_rrn_length(self):
        with self.assertRaises(ValidationError):
            validate(self.data + 'a', self.schema, format_checker=FormatChecker())


MISC_CODE_REGEX = r"[A-Z]{2}[0-9]{3}[A-Z][0-9]{8}"


class TestJoinedString(TestCase):
    def setUp(self) -> None:
        self.misc_codes = ['KR049A20000024', 'KR049A20000025', 'KR049A20000026', 'KR049A20000027']
        self.schema = JsonSchema.joined_string(separator=',', pattern_of_piece=MISC_CODE_REGEX)

    def test_success(self):
        data = ','.join(self.misc_codes)

        validate(data, self.schema, format_checker=FormatChecker())

    def test_failure_when_separator_is_invalid(self):
        data = '|'.join(self.misc_codes)

        with self.assertRaises(ValidationError):
            validate(data, self.schema, format_checker=FormatChecker())

    def test_failure_when_separator_is_blank(self):
        data = ''.join(self.misc_codes)

        with self.assertRaises(ValidationError):
            validate(data, self.schema, format_checker=FormatChecker())

    def test_failure_when_dabs_code_is_invalid(self):
        self.misc_codes.append('invalid_dabs')
        data = ','.join(self.misc_codes)

        with self.assertRaises(ValidationError):
            validate(data, self.schema, format_checker=FormatChecker())


class TestJoinedStringFromEnum(TestCase):
    def setUp(self) -> None:
        self.enums = [CredentialsType.SERVICE_CREDENTIALS.value, CredentialsType.USER_CREDENTIALS.value]
        self.schema = JsonSchema.joined_string_from_enum(CredentialsType)

    def test_success(self):
        data = ','.join(self.enums)
        validate(data, self.schema, format_checker=FormatChecker())

    def test_failure_when_separator_is_invalid(self):
        data = '|'.join(self.enums)

        with self.assertRaises(ValidationError):
            validate(data, self.schema, format_checker=FormatChecker())

    def test_failure_when_separator_is_blank(self):
        data = ''.join(self.enums)

        with self.assertRaises(ValidationError):
            validate(data, self.schema, format_checker=FormatChecker())

    def test_failure_when_enum_is_invalid(self):
        self.enums.append('invalid_enum')
        data = ','.join(self.enums)

        with self.assertRaises(ValidationError):
            validate(data, self.schema, format_checker=FormatChecker())


class TestFromEnumKebabSchema(TestCase):
    class TestEnum(Enum):
        TEST_FOO_BAR = 'test_foo_bar'

    def setUp(self) -> None:
        self.data = 'test-foo-bar'
        self.schema = JsonSchema.from_enum(self.TestEnum, accept_kebab_only=True)

    def test_enum(self):
        validate(self.data, self.schema, format_checker=FormatChecker())

    def test_enum_snake_type(self):
        with self.assertRaises(ValidationError):
            validate(stringcase.snakecase(self.data), self.schema, format_checker=FormatChecker())

import dataclasses
from unittest import TestCase
from unittest.mock import patch

from utils import logging


@dataclasses.dataclass
class _Data:
    key: str


@patch('utils.logging._logger')
class TestLogging(TestCase):
    def setUp(self) -> None:
        self.expected_msg = 'msg'
        self.data = _Data(key='val')
        self.expected_data = dataclasses.asdict(self.data)

    def test_info(self, logger):
        logging.info(msg=self.expected_msg,
                     data=self.data)

        logger.info.assert_called_once_with('test_info',
                                            msg=self.expected_msg,
                                            data=self.expected_data)

    def test_debug(self, logger):
        logging.debug(msg=self.expected_msg,
                      data=self.data)

        logger.debug.assert_called_once_with('test_debug',
                                             msg=self.expected_msg,
                                             data=self.expected_data)

    def test_warn(self, logger):
        logging.warn(msg=self.expected_msg,
                     data=self.data)

        logger.warn.assert_called_once_with('test_warn',
                                            msg=self.expected_msg,
                                            data=self.expected_data)

    def test_error(self, logger):
        logging.error(msg=self.expected_msg,
                      data=self.data,
                      err=RuntimeError)

        logger.error.assert_called_once_with('test_error',
                                             msg=self.expected_msg,
                                             data=self.expected_data,
                                             err=RuntimeError)

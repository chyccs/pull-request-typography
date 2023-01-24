import inspect
from typing import Any

import structlog

_logger = structlog.getLogger()


def __get_caller_name():
    return str(inspect.stack()[2][3])


def __parse_data_to_dict(data: Any):
    return (data
            if not data
            or data is dict
            or not getattr(data, '__dict__', None) else data.__dict__)


def info(msg: str, data: Any = None):
    _logger.info(__get_caller_name(), msg=msg, data=__parse_data_to_dict(data) if data else None)


def debug(msg: str, data: Any = None):
    _logger.debug(__get_caller_name(), msg=msg, data=__parse_data_to_dict(data) if data else None)


def warn(msg: str, data: Any = None):
    _logger.warn(__get_caller_name(), msg=msg, data=__parse_data_to_dict(data) if data else None)


def error(msg: str, err=None, data: Any = None):
    _logger.error(__get_caller_name(), msg=msg, data=__parse_data_to_dict(data) if data else None, err=err)

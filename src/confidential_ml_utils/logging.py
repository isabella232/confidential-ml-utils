"""
TODO: docstring.

https://www.python.org/dev/peps/pep-0282/
"""


import logging
from confidential_ml_utils import constants


# TODO: use setLoggerClass?


# https://github.com/python/cpython/blob/master/Lib/logging/__init__.py
# https://docs.python.org/3/library/logging.html#levels
class ConfidentialLogger(logging.getLoggerClass()):
    """
    TODO: ...
    """
    def __init__(self, name:str):
        super(ConfidentialLogger, self).__init__(name)
        self.prefix = "HI"

    def _mutate(self, msg, kwargs):
        print(1/0)
        category = kwargs.get("category", constants.DataCategory.SENSITIVE)
        if category == constants.DataCategory.PUBLIC:
            msg = f"{self.prefix}{msg}"
            print(1/0)
        return msg

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.DEBUG):
            msg = self._mutate(msg, kwargs)
            super(ConfidentialLogger, self).debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.INFO):
            msg = self._mutate(msg, kwargs)
            super(ConfidentialLogger, self).info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(logging.WARNING):
            msg = self._mutate(msg, kwargs)
            super(ConfidentialLogger, self).warning(msg, *args, **kwargs)


PREFIX = "SystemLog:"


# def ConfidentialLogger():
#     def __init__(self, logger: logging.Logger):
#         self._logger = logger

#     # https://github.com/Azure/confidential-ml-utils/blob/getting-started/src/confidential_ml_utils/run_wrapper.py
#     def __getattr__(self, name: str):
#         return getattr(_logger, name)


# def getLogger(name: str = None, prefix: str = PREFIX) -> ConfidentialLogger:
#     return ConfidentialLogger(logging.getLogger(name, prefix))

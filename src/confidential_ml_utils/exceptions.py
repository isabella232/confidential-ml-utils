# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
Decorators and utilities for prefixing exception stack traces while obscuring
the exception message itself.
"""


import argparse
import functools
import re
import sys
import time
from traceback import TracebackException

# https://stackoverflow.com/a/38569536
from typing import Callable, Optional, TextIO


PREFIX = "SystemLog:"
SCRUB_MESSAGE = "**Exception message scrubbed**"


class PublicValueError(ValueError):
    """
    Value error with public message. Exceptions of this type raised under
    `prefix_stack_trace` or `print_prefixed_stack_trace_and_raise` will have
    the message prefixed with `PREFIX` in both the printed stack trace and the
    re-raised exception.
    """


class PublicRuntimeError(RuntimeError):
    """
    Runtime error with public message. Exceptions of this type raised under
    `prefix_stack_trace` or `print_prefixed_stack_trace_and_raise` will have
    the message prefixed with `PREFIX` in both the printed stack trace and the
    re-raised exception.
    """


class PublicArgumentError(argparse.ArgumentError):
    """
    Argument error with public message. Exceptions of this type raised under
    `prefix_stack_trace` or `print_prefixed_stack_trace_and_raise` will have
    the message prefixed with `PREFIX` in both the printed stack trace and the
    re-raised exception.
    """


default_allow_list = [
    PublicValueError.__name__,
    PublicRuntimeError.__name__,
    PublicArgumentError.__name__,
]


def scrub_exception_traceback(
    exception: TracebackException,
    scrub_message: str = SCRUB_MESSAGE,
    allow_list: list = [],
) -> TracebackException:
    """
    Scrub exception messages from a `TracebackException` object. The messages
    will be replaced with `exceptions.SCRUB_MESSAGE`.
    """
    if not is_exception_allowed(exception, allow_list):
        exception._str = scrub_message  # type: ignore
    if exception.__cause__:
        exception.__cause__ = scrub_exception_traceback(
            exception.__cause__, scrub_message, allow_list
        )
    if exception.__context__:
        exception.__context__ = scrub_exception_traceback(
            exception.__context__, scrub_message, allow_list
        )
    return exception


def is_exception_allowed(exception: TracebackException, allow_list: list) -> bool:
    """
    Check if message is allowed, either by `allow_list`, or `default_allow_list`.

    Args:
        exception (TracebackException): the exception to test
        allow_list (list): list of regex expressions. If any expression matches
            the exception name or message, it will be considered allowed.

    Returns:
        bool: True if message is allowed, False otherwise.
    """
    # empty list means all messages are allowed
    for expr in allow_list + default_allow_list:
        if re.search(expr, exception._str, re.IGNORECASE):  # type: ignore
            return True
        if re.search(expr, exception.exc_type.__name__, re.IGNORECASE):
            return True
    return False


def _rethrow_with_transformed_string_args(
    err: Optional[BaseException], prefix: str, transform: Callable[[str], str]
):
    """
    Safely re-throw the exception `err`, transforming all **string**-valued
    arguments using `transform`. Properly handle the cases a) `err` is `None`,
    b) `err` does not have any `args`, c) `err` has non-string-valued args.
    """
    if not getattr(err, "args", None):
        raise type(err)() from err
    else:
        new_args = [
            f"{prefix} {transform(arg)}" if isinstance(arg, str) else arg
            for arg in err.args
        ]
        raise type(err)(*new_args) from err


def print_prefixed_stack_trace_and_raise(
    file: TextIO = sys.stderr,
    prefix: str = PREFIX,
    scrub_message: str = SCRUB_MESSAGE,
    keep_message: bool = False,
    allow_list: list = [],
    add_timestamp: bool = False,
    err: Optional[BaseException] = None,
) -> None:
    """
    Print the current exception and stack trace to `file` (usually client
    standard error), prefixing the stack trace with `prefix`.
    Args:
        keep_message (bool): if True, don't scrub message. If false, scrub (unless
            allowed).
        allow_list (list): exception allow_list. Ignored if keep_message is True. If
            empty all messages will be srubbed.
        err: the error that was thrown. None accepted for backwards compatibility.
    """
    # scrub the log
    exception = TracebackException(*sys.exc_info())  # type: ignore
    if keep_message:
        scrubbed_exception = exception
    else:
        scrubbed_exception = scrub_exception_traceback(
            exception, scrub_message, allow_list
        )
    traceback = list(scrubbed_exception.format())
    for execution in traceback:
        if "return function(*func_args, **func_kwargs)" in execution:
            # Do not show the stack trace for our decorator.
            continue
        lines = execution.splitlines()
        for line in lines:
            if add_timestamp:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f"{prefix} {current_time} {line}", file=file)
            else:
                print(f"{prefix} {line}", file=file)

    # raise compliant error
    if not err:
        raise Exception()
    elif keep_message or is_exception_allowed(exception, allow_list):
        _rethrow_with_transformed_string_args(err, prefix, lambda arg: arg)
    else:
        _rethrow_with_transformed_string_args(err, prefix, lambda _: scrub_message)


class _PrefixStackTraceWrapper:
    """
    Callable object for catching exceptions and printing their stack traces,
    appropriately prefixed.

    This is an object instead of a nested function to support working in Spark.
    Python anonymous functions are not "pickleable", so we need to define a
    class which handles this logic, so the class is picklable.
    """

    def __init__(
        self,
        file: TextIO,
        disable: bool,
        prefix: str,
        scrub_message: str,
        keep_message: bool,
        allow_list: list,
        add_timestamp: bool,
    ) -> None:
        self.allow_list = allow_list
        self.disable = disable
        self.file = file
        self.keep_message = keep_message
        self.prefix = prefix
        self.scrub_message = scrub_message
        self.add_timestamp = add_timestamp

    def __call__(self, function) -> Callable:
        @functools.wraps(function)
        def wrapper(*func_args, **func_kwargs):
            """
            Create a wrapper which catches exceptions thrown by `function`,
            scrub exception messages, and logs the prefixed stack trace.
            """
            try:
                return function(*func_args, **func_kwargs)
            except BaseException as err:
                print_prefixed_stack_trace_and_raise(
                    self.file,
                    self.prefix,
                    self.scrub_message,
                    self.keep_message,
                    self.allow_list,
                    self.add_timestamp,
                    err,
                )

        return function if self.disable else wrapper


def prefix_stack_trace(
    file: TextIO = sys.stderr,
    disable: bool = bool(sys.flags.debug),
    prefix: str = PREFIX,
    scrub_message: str = SCRUB_MESSAGE,
    keep_message: bool = False,
    allow_list: list = [],
    add_timestamp: bool = False,
) -> Callable:
    """
    Decorator which wraps the decorated function and prints the stack trace of
    exceptions which occur, prefixed with `prefix` and with exception messages
    scrubbed (replaced with `scrub_message`). To use this, just add
    `@prefix_stack_trace()` above your function definition, e.g.

        @prefix_stack_trace()
        def foo(x):
            pass
    """

    return _PrefixStackTraceWrapper(
        file, disable, prefix, scrub_message, keep_message, allow_list, add_timestamp
    )


class PrefixStackTrace:
    def __init__(
        self,
        file: TextIO = sys.stderr,
        disable: bool = bool(sys.flags.debug),
        prefix: str = PREFIX,
        scrub_message: str = SCRUB_MESSAGE,
        keep_message: bool = False,
        add_timestamp: bool = False,
        allow_list: list = [],
    ):
        self.file = file
        self.disable = disable
        self.prefix = prefix
        self.scrub_message = scrub_message
        self.keep_message = keep_message
        self.add_timestamp = add_timestamp
        self.allow_list = allow_list

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and not self.disable:
            print_prefixed_stack_trace_and_raise(
                file=self.file,
                prefix=self.prefix,
                scrub_message=self.scrub_message,
                keep_message=self.keep_message,
                allow_list=self.allow_list,
                add_timestamp=self.add_timestamp,
                err=exc_value,
            )

"""
Decorators and utilities for prefixing exception stack traces while obscuring
the exception message itself.
"""


import functools
import io
from traceback import TracebackException
from typing import Callable
import sys


PREFIX = "SystemLog:"
SCRUB_MESSAGE = "**Exception message scrubbed**"


def scrub_exception_traceback(
    exception: TracebackException, scrub_message: str
) -> TracebackException:
    """
    Scrub exception messages from a `TracebackException` object. The messages
    will be replaced with `exceptions.PREFIX`.
    """
    exception._str = scrub_message
    if exception.__cause__:
        exception.__cause__ = scrub_exception_traceback(
            exception.__cause__, scrub_message
        )
    if exception.__context__:
        exception.__context__ = scrub_exception_traceback(
            exception.__context__, scrub_message
        )
    return exception


def print_prefixed_stack_trace(
    file: io.TextIOBase, prefix: str, scrub_message: str
) -> None:
    """
    Print the current exception and stack trace to `file` (usually client
    standard error), prefixing the stack trace with `prefix`.
    """
    exception = TracebackException(*sys.exc_info())
    scrubbed_exception = scrub_exception_traceback(exception, scrub_message)
    traceback = list(scrubbed_exception.format())
    for execution in traceback:
        if "return function(*func_args, **func_kwargs)" in execution:
            # Do not show the stack trace for our decorator.
            continue
        lines = execution.splitlines()
        for line in lines:
            print(f"{prefix} {line}", file=file)


def prefix_stack_trace(
    file: io.TextIOBase = sys.stderr,
    disable: bool = sys.flags.debug,
    prefix: str = PREFIX,
    scrub_message: str = SCRUB_MESSAGE,
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

    def decorator(function: Callable) -> Callable:
        """
        Create a decorator to catch, modify, and log an exception with its
        stack trace. Follows:
        https://www.blog.pythonlibrary.org/2016/06/09/python-how-to-create-an-exception-logging-decorator/
        """

        @functools.wraps(function)
        def wrapper(*func_args, **func_kwargs):
            """
            Create a wrapper which catches exceptions thrown by `function`,
            scrub exception messages, and logs the prefixed stack trace.
            """
            try:
                return function(*func_args, **func_kwargs)
            except BaseException:
                print_prefixed_stack_trace(file, prefix, scrub_message)
                raise

        return function if disable else wrapper

    return decorator

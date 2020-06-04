import functools
import io
from traceback import TracebackException
from typing import Callable
import sys


SCRUB_MESSAGE = "**Exception message scrubbed**"


def scrub_traceback(traceback: TracebackException) -> TracebackException:
    traceback._str = SCRUB_MESSAGE
    if traceback.__cause__:
        traceback.__cause__ = scrub_traceback(traceback.__cause__)
    if traceback.__context__:
        traceback.__context__ = scrub_traceback(traceback.__context__)
    return traceback


def print_prefixed_stack_trace(file: io.TextIOBase, prefix: str) -> None:
    """
    TODO: docstring.
    """
    traceback = TracebackException(*sys.exc_info())
    scrubbed_traceback = scrub_traceback(traceback)
    list_traceback = list(scrubbed_traceback.format())
    for exc in list_traceback:
        if "return function(*func_args, **func_kwargs)" in exc:
            # TODO: why?
            continue
        lines = exc.splitlines()
        for line in lines:
            print(f"{prefix} {line}", file=file)


def prefix_stack_trace(
    file: io.TextIOBase = sys.stderr,
    disable: bool = sys.flags.debug,
    prefix: str = "SystemLog:",
) -> Callable:
    """
    TODO: docstring.
    """

    def decorator(function: Callable) -> Callable:
        """
        TODO: docstring.
        """

        @functools.wraps(function)
        def wrapper(*func_args, **func_kwargs):
            try:
                return function(*func_args, **func_kwargs)
            except BaseException:
                print_prefixed_stack_trace(file, prefix)
                raise

        return function if disable else wrapper

    return decorator

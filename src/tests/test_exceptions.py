# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import io
import pytest
from confidential_ml_utils.exceptions import (
    prefix_stack_trace,
    SCRUB_MESSAGE,
    PREFIX,
    is_exception_allowed,
    PrefixStackTrace,
)
from traceback import TracebackException


@pytest.mark.parametrize(
    "message,exec_type",
    [("foo", ArithmeticError), ("secret data", KeyError), ("baz", Exception)],
)
def test_prefix_stack_trace_preserves_exception_type(message: str, exec_type):
    """
    Verify that the exception type and "scrub message" appear in the
    prefixed lines.
    """
    file = io.StringIO()

    @prefix_stack_trace(file)
    def function():
        raise exec_type(message)

    with pytest.raises(exec_type):
        function()

    log_lines = file.getvalue()
    assert exec_type.__name__ in log_lines
    assert SCRUB_MESSAGE in log_lines


def test_prefix_stack_trace_succeeds_when_no_message():
    """
    Verify that exceptions without message are re-raised correctly.
    """
    file = io.StringIO()

    @prefix_stack_trace(file, keep_message=True)
    def function():
        assert False

    with pytest.raises(AssertionError):
        function()

    log_lines = file.getvalue()
    assert AssertionError.__name__ in log_lines


def test_prefix_stack_trace_respects_disable():
    """
    Verify that the parameter `disable` of `prefix_stack_trace` turns off the
    functionality that decorator implements.
    """
    file = io.StringIO()

    @prefix_stack_trace(file, disable=True)
    def function():
        raise Exception()

    with pytest.raises(Exception):
        function()

    assert file.getvalue() == ""


@pytest.mark.parametrize("prefix", ["foo__"])
def test_prefix_stack_trace_respects_prefix(prefix):
    """
    Verify that the prefix added in by `prefix_stack_trace` respects the
    provided configuration.
    """
    file = io.StringIO()

    @prefix_stack_trace(file, prefix=prefix)
    def function():
        raise Exception()

    with pytest.raises(Exception):
        function()

    assert prefix in file.getvalue()


@pytest.mark.parametrize(
    "disable,prefix,message", [(False, "pref", "mess"), (True, "foo", "bar")]
)
def test_prefix_stack_trace_respects_scrub_message(disable, prefix, message):
    """
    Verify that the "message scrubbed" string added in by `prefix_stack_trace`
    respects the provided configuration.
    """
    file = io.StringIO()

    def function():
        raise Exception(message)

    with pytest.raises(Exception):
        with PrefixStackTrace(
            disable=disable, prefix=prefix, scrub_message=message, file=file
        ):
            function()

    file_value = file.getvalue()
    if disable:
        assert "" == file_value
    else:
        assert prefix in file_value
        assert message in file_value


@pytest.mark.parametrize(
    "keep_message, allow_list, expected_result",
    [
        (
            False,
            ["arithmetic", "ModuleNotFound"],
            True,
        ),  # scrub_message with allow_list
        (False, [], False),  # scrub_message
        (True, [], True),
    ],
)  # keep_message
def test_prefix_stack_trace_nested_exception(keep_message, allow_list, expected_result):
    file = io.StringIO()

    def function1():
        import my_custom_library

        my_custom_library.foo()

    @prefix_stack_trace(file, keep_message=keep_message, allow_list=allow_list)
    def function2():
        try:
            function1()
        except ModuleNotFoundError:
            raise ArithmeticError()

    with pytest.raises(Exception):
        function2()

    assert ("No module named" in file.getvalue()) == expected_result


@pytest.mark.parametrize(
    "allow_list, expected_result",
    [
        (["ModuleNotFound"], True),  # allow_list match error type
        (["arithmetic", "ModuleNotFound"], True),  # allow_list multiple strings
        (["geometry", "algebra"], False),  # allow_list no match
        (["my_custom_library"], True),  # allow_list match error message
    ],
)
def test_prefix_stack_trace_allow_list(allow_list, expected_result):
    file = io.StringIO()
    message = "No module named"

    @prefix_stack_trace(file, allow_list=allow_list)
    def function():
        import my_custom_library

        my_custom_library.foo()

    with pytest.raises(Exception):
        function()

    assert (message in file.getvalue()) == expected_result


@pytest.mark.parametrize(
    "allow_list, expected_result",
    [
        (["argparse", "ModuleNotFound"], True),
        (["argparse", "type"], False),
        (["Bingo..+Pickle"], True),
        ([], False),
    ],
)
def test_is_exception_allowed(allow_list, expected_result):
    exception = ModuleNotFoundError("Bingo. It is a pickle.")
    res = is_exception_allowed(TracebackException.from_exception(exception), allow_list)
    assert res == expected_result


@pytest.mark.parametrize(
    "keep_message, allow_list",
    [
        (True, []),  # unscrub message
        (False, []),  # scrub message
        (False, ["ValueError"]),  # unscrub whitelisted message
    ],
)
def test_prefix_stack_trace_throws_correctly(keep_message, allow_list):
    """
    After logging the library continues execution by rethrowing an error. The final
    error thrown is picked up for error reporting by AML. It should be consistent
    with user's scrubbing choice. Verify that the scrubber preserves the exception type
    and correctly modifies the exception message
    """
    file = io.StringIO()

    message = "This is the original exception message"
    e_type = ValueError

    @prefix_stack_trace(file, keep_message=keep_message, allow_list=allow_list)
    def function():
        raise e_type(message)

    with pytest.raises(ValueError) as info:
        function()

    if keep_message is True or is_exception_allowed(
        TracebackException.from_exception(info.value), allow_list
    ):
        assert message in str(info.value)
    else:
        assert SCRUB_MESSAGE in str(info.value)

    assert PREFIX in str(info.value)
    assert info.type == e_type

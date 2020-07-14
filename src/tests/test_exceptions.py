import io
import pytest
from confidential_ml_utils.exceptions import (
    prefix_stack_trace,
    SCRUB_MESSAGE,
    is_exception_whitelisted,
)
from traceback import TracebackException


@pytest.mark.parametrize(
    "message,exec_type",
    [("foo", ArithmeticError), ("secret data", KeyError), ("baz", Exception)],
)
def test_prefix_stack_trace_preserves_exception_type(message: str, exec_type):
    """
    Verify that the exception type and "scrub message" appear in the
    prefixed lines. Also, verify that the `prefix_stack_trace` decorator does
    not modify the type and message of the exception which is thrown.
    """
    file = io.StringIO()

    @prefix_stack_trace(file)
    def function():
        raise exec_type(message)

    with pytest.raises(exec_type) as info:
        function()

    assert message in str(info.value)
    log_lines = file.getvalue()
    assert exec_type.__name__ in log_lines
    assert SCRUB_MESSAGE in log_lines


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


@pytest.mark.parametrize("message", ["foo__"])
def test_prefix_stack_trace_respects_scrub_message(message):
    """
    Verify that the "message scrubbed" string added in by `prefix_stack_trace`
    respects the provided configuration.
    """
    file = io.StringIO()

    @prefix_stack_trace(file, scrub_message=message)
    def function():
        raise Exception()

    with pytest.raises(Exception):
        function()

    assert message in file.getvalue()


@pytest.mark.parametrize(
    "keep_message, whitelist, expected_result",
    [
        (False, ["arithmetic", "ModuleNotFound"], True),  # scrub_message with whitelist
        (False, [], False),  # scrub_message
        (True, [], True),
    ],
)  # keep_message
def test_prefix_stack_trace_nested_exception(keep_message, whitelist, expected_result):
    file = io.StringIO()

    def function1():
        import my_custom_library

    @prefix_stack_trace(file, keep_message=keep_message, whitelist=whitelist)
    def function2():
        try:
            function1()
        except ModuleNotFoundError:
            raise ArithmeticError()

    with pytest.raises(Exception):
        function2()

    assert ("No module named" in file.getvalue()) == expected_result


@pytest.mark.parametrize(
    "whitelist, expected_result",
    [
        (["ModuleNotFound"], True),  # whitelist match error type
        (["arithmetic", "ModuleNotFound"], True),  # whitelist multiple strings
        (["geometry", "algebra"], False),  # whitelist no match
        (["my_custom_library"], True),
    ],
)  # whitelist match error message
def test_prefix_stack_trace_whitelist(whitelist, expected_result):
    file = io.StringIO()
    message = "No module named"

    @prefix_stack_trace(file, whitelist=whitelist)
    def function():
        import my_custom_library

    with pytest.raises(Exception):
        function()

    assert (message in file.getvalue()) == expected_result


@pytest.mark.parametrize(
    "whitelist, expected_result",
    [
        (["argparse", "ModuleNotFound"], True),
        (["argparse", "type"], False),
        (["Bingo..+Pickle"], True),
        ([], False),
    ],
)
def test_is_exception_whitelisted(whitelist, expected_result):
    exception = ModuleNotFoundError("Bingo. It is a pickle.")
    res = is_exception_whitelisted(
        TracebackException.from_exception(exception), whitelist
    )
    assert res == expected_result

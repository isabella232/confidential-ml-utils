import io
import pytest
from confidential_ml_utils.exceptions import prefix_stack_trace, SCRUB_MESSAGE


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

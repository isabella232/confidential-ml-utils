import io
import pytest
from confidential_ml_utils.exceptions import prefix_stack_trace, SCRUB_MESSAGE


@pytest.mark.parametrize(
    "message,exec_type",
    [("foo", ArithmeticError), ("secret data", KeyError), ("baz", Exception)],
)
def test_prefix_stack_trace_preserves_exception_type(message: str, exec_type):
    file = io.StringIO()

    @prefix_stack_trace(file)
    def function():
        raise exec_type(message)

    with pytest.raises(exec_type) as info:
        function()

    assert message in str(info.value)
    assert SCRUB_MESSAGE in file.getvalue()


def test_prefix_stack_trace_respects_disable():
    file = io.StringIO()

    @prefix_stack_trace(file, disable=True)
    def function():
        raise Exception()

    with pytest.raises(Exception):
        function()

    assert file.getvalue() == ""


@pytest.mark.parametrize("prefix", ["foo__"])
def test_prefix_stack_trace_respects_prefix(prefix):
    file = io.StringIO()

    @prefix_stack_trace(file, prefix=prefix)
    def function():
        raise Exception()

    with pytest.raises(Exception):
        function()

    assert prefix in file.getvalue()


@pytest.mark.parametrize("message", ["foo__"])
def test_prefix_stack_trace_respects_scrub_message(message):
    file = io.StringIO()

    @prefix_stack_trace(file, scrub_message=message)
    def function():
        raise Exception()

    with pytest.raises(Exception):
        function()

    assert message in file.getvalue()

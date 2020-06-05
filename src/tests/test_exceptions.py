import io
import pytest
from confidential_ml_utils.exceptions import *


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

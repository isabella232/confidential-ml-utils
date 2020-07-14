## Exception Handling

First execute `pip install confidential-ml-utils` to install this library. Then
wrap any methods which may throw an exception with the decorator
`prefix_stack_trace`. Here's a simple example.

```python
from confidential_ml_utils.exceptions import prefix_stack_trace

@prefix_stack_trace()
def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
```

## Examples

The simplest use case (wrap your `main` method in a decorator) is in:
[hello-world.py](./hello-world.py).

Some configuration options around prefixing the stack trace. [prefix-stack-trace.py](./prefix-stack-trace.py). You can:
-  customize the prefix and the exception message
-  keep the original exception message (don't scrub)
-  pass an allow_list of strings. Exception messages will be scrubbed unless the message or the
exception type regex match one of the allow_list strings.

Using this library directly inside `try` / `except` statements:
[try-except.py](./try-except.py)

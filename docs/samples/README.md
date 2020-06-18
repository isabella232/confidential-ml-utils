# Sample usage

This directory contains lightweight Python scripts demonstrating different
uses of the confidential ML utilities library. To run any of these, first
execute

```
pip install confidential-ml-utils
```

## Exception Handling

The simplest use case (wrap your `main` method in a decorator) is in:
[hello-world.py](./hello-world.py).

Some configuration options around prefixing the stack trace:
[prefix-stack-trace.py](./prefix-stack-trace.py).

Using this library directly inside `try` / `except` statements:
[try-except.py](./try-except.py)

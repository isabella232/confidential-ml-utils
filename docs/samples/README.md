# Sample usage

## Exception handling

```python
from confidential_ml_utils.exceptions import prefix_stack_trace

@prefix_stack_trace()
def my_function(args):
    # real logic here.
    pass

@prefix_stack_trace(prefix = "MyCustomPrefix")
def my_other_function(args):
    # Real logic.
    pass
```

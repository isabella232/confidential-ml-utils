"""
Simple script with examples of how to directly use the function
print_prefixed_stack_trace to capture information about failed module imports.
"""

from confidential_ml_utils.exceptions import print_prefixed_stack_trace

try:
    # Import statement which could raise an exception containing sensitive
    # data.
    import my_custom_library
except:
    # Output will be:
    #
    # SystemLog: Traceback (most recent call last):
    # SystemLog:   File ".\try-except.py", line 10, in <module>
    # SystemLog:     import my_custom_library
    # SystemLog: ModuleNotFoundError: **Exception message scrubbed**
    print_prefixed_stack_trace()

try:
    # Import statement which will never raise an exception containing sensitive
    # data.
    import another_custom_library
except:
    # Output will be:
    #
    # SystemLog: Traceback (most recent call last):
    # SystemLog:   File ".\try-except.py", line 17, in <module>
    # SystemLog:     import another_custom_library
    # SystemLog: ModuleNotFoundError: No module named 'another_custom_library'
    print_prefixed_stack_trace(keep_message=True)

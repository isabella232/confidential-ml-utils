"""
Demonstrate how scrubbing options.
"""

from confidential_ml_utils.exceptions import prefix_stack_trace

# Output will be:
#
# MyCustomPrefix Traceback (most recent call last):
# MyCustomPrefix   File ".\prefix-stack-trace.py", line 11, in main
# MyCustomPrefix     print(1 / 0)
# MyCustomPrefix ZeroDivisionError: **Exception message scrubbed**
@prefix_stack_trace(prefix="MyCustomPrefix")
def custom_prefix():
    print(1 / 0)


# Output will be:
#
# SystemLog: Traceback (most recent call last):
# SystemLog:   File "/mnt/c/code/confidential-ml-utils/docs/samples/prefix-stack-trace.py", line 20, in scrub2
# SystemLog:     print(1 / 0)
# SystemLog: ZeroDivisionError: Private data was divided by zero
@prefix_stack_trace(scrub_message="Private data was divided by zero")
def custom_message():
    print(1 / 0)


# Output will be:
#
# SystemLog: Traceback (most recent call last):
# SystemLog:   File "/mnt/c/code/confidential-ml-utils/docs/samples/prefix-stack-trace.py", line 24, in scrub3
# SystemLog:     print(1 / 0)
# SystemLog: ZeroDivisionError: division by zero
@prefix_stack_trace(keep_message=True)
def keep_exception_message():
    print(1 / 0)


# Output will be:
#
# SystemLog: Traceback (most recent call last):
# SystemLog:   File "/mnt/c/code/confidential-ml-utils/docs/samples/prefix-stack-trace.py", line 28, in scrub4
# SystemLog:     print(1 / 0)
# SystemLog: ZeroDivisionError: division by zero
@prefix_stack_trace(keep_message=False, allow_list=["ZeroDivision"])
def keep_allowed_exceptions():
    print(1 / 0)


if __name__ == "__main__":
    try:
        custom_prefix()
    except:
        pass
    try:
        custom_message()
    except:
        pass
    try:
        keep_exception_message()
    except:
        pass
    try:
        keep_allowed_exceptions()
    except:
        pass


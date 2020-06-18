"""
Demonstrate how the prefix can be customized.
"""

from confidential_ml_utils.exceptions import prefix_stack_trace


# Output will be:
#
# MyCustomPrefix Traceback (most recent call last):
# MyCustomPrefix   File ".\prefix-stack-trace.py", line 11, in main
# MyCustomPrefix     print(1 / 0)
# MyCustomPrefix ZeroDivisionError: **Exception message scrubbed**
@prefix_stack_trace(prefix="MyCustomPrefix")
def main():
    print("Hello, world!")
    print(1 / 0)


if __name__ == "__main__":
    main()

# Logging in confidential ML

Need to distinguish between "safe" logs (list a directory, print a metric) and
"unsafe" logs (print a line of customer data). User should be forced to make
that distinction every time they log, if there is a default it is for the
log line to be "unsafe".

The "safe" logger should mutate the log line to get it through scrubbers.

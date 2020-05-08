"""
Utility classes for argument parsing
"""
import logging
import argparse
import sys
import errno

from .constants import DataCategory

class CompliantArgumentParser(argparse.ArgumentParser):
    """ ArgumentParser that sends message to logs when parsing fails. """
    def error(self, message):
        """Upon argument parsing error, throws an ArgumentParserError exception.

        Args:
            message (str): error message from argparse

        Raises:
            ArgumentParserError: an error occured during argument parsing
        """
        log(logging.CRITICAL, DataCategory.ONLY_PUBLIC_DATA, message)
        sys.exit(errno.EINVAL)

    def parse_known_args(self, args=None, namespace=None):
        """ Sometimes a script may only parse a few of the command-line
        arguments, passing the remaining arguments on to another script
        or program. In these cases, the parse_known_args() method can be
        useful. It works much like parse_args() except that it does not
        produce an error when extra arguments are present. Instead, it
        returns a two item tuple containing the populated namespace and
        the list of remaining argument strings. """
        args, unknown_args = super().parse_known_args(args=args, namespace=namespace)

        if unknown_args: # if list of unknown arguments is not empty
            log(logging.WARNING, DataCategory.ONLY_PUBLIC_DATA, "Following arguments provided cannot be recognized: {}".format(unknown_args))

        return args, unknown_args

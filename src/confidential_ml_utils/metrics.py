"""
    Metrics reporting
"""
import logging
import sys
import os
import time
import tempfile
from functools import wraps

from .constants import DataCategory
from .logging import log
from .run_wrapper import AmlRunWrapper

def log_directory(data_category, key, path, verbose=False):
    """ Counts files, dirs, size in a given directory and record
    as AML metric (or StdOut)

    Args:
        data_category (DataCategory) : public or private?
        key (string) : metric identifier in step run
        path (string) : path to directory to scan
        verbose (bool) : list all files in directory as metrics
    """
    run = AmlRunWrapper()

    count_files = 0
    count_dirs = 0
    total_size = 0
    for base_dir, subdirs, files in os.walk(path):
        count_dirs += len(subdirs)
        count_files += len(files)
        for entry in files:
            entry_size = os.path.getsize(os.path.join(base_dir, entry))
            total_size += entry_size
            if verbose:
                log(logging.INFO, data_category, "Scan {} -- found file: {} -- size {}".format(key, os.path.join(base_dir, entry), entry_size))

    run.log_row(key, dirs=count_dirs, files=count_files, size=total_size)

    log(logging.INFO, data_category, "Scan {} -- path {} -- found {} files, {} dirs, total size {}".format(
        key, path, count_files, count_dirs, total_size
    ))

def log_metric(data_category, key, value):
    """ to use accross user code """
    if data_category == DataCategory.ONLY_PUBLIC_DATA:
        # if public, ask azureml to record (if azureml attached)
        run = AmlRunWrapper()
        run.log(key, value)
    else:
        # if unsure, just print in logs
        log(logging.INFO, data_category, "Metric({}={})".format(key, value))

def log_row(data_category, key, **kwargs):
    """ to use accross user code """
    if data_category == DataCategory.ONLY_PUBLIC_DATA:
        # if public, ask azureml to record (if azureml attached)
        run = AmlRunWrapper()
        run.log_row(key, **kwargs)
    else:
        # if unsure, just print in logs
        log(logging.INFO, data_category, "MetricRow({}, {})".format(key, kwargs))


########################
### CODE BLOCK TIMER ###
########################

class log_time_block(object):
    """ This class should be used to time a code block.
    The time diff is computed from __enter__ to __exit__
    and can be:
    - printed out (see kwargs verbose)
    - logged as metric in a run (see kwargs run)
    - added to a dictionary (see kwargs profile)

    Example
    -------
    >>> job_profile = {}
    >>> with log_time_block("my_perf_metric_name", profile=job_profile, verbose=True):
            print("(((sleeping for 1 second)))")
            time.sleep(1)
    --- time elapsted my_perf_metric_name : 1.0 s
    >>> job_profile
    { 'my_perf_metric_name': 1.0 }
    """

    def __init__(self, name, **kwargs):
        """
        Constructs the log_time_block.

        Arguments
        ---------
        name: {str}
            key for the time difference (for storing as metric)

        Keyword Arguments
        -----------------
        print: {bool}
            prints out time with print()
        run: {azureml.core.run.Run}
            sends time to a specific AzureML Run via run.log(name, time)
            if not provided, uses (if any) the one provided during recipe_log_setup()
        profile: {dict}
            stores the time in a given dictionary
        tags: {dict}
            add properties to metrics for logging as log_row()
        """
        # kwargs
        self.print = kwargs.get('print', False)
        self.run = kwargs.get('run', AmlRunWrapper())
        self.profile = kwargs.get('profile', None)
        self.tags = kwargs.get('tags', None)

        # internal variables
        self.name = name
        self.start_time = None

    def __enter__(self):
        """ Starts the timer, gets triggered at beginning of code block """
        self.start_time = time.time() # starts "timer"

    def __exit__(self, exc_type, value, traceback):
        """ Stops the timer and stores accordingly
        gets triggered at beginning of code block.
        Note: arguments are by design for with statements. """
        run_time = time.time() - self.start_time # stops "timer"

        if self.run:
            # if run provided, sends to AzureML as log
            if self.tags:
                self.tags[self.name] = run_time
                self.run.log_row(self.name, **self.tags)
            else:
                self.run.log(self.name, run_time)

        if self.profile:
            # if profile dict is provided, stores the value
            self.profile[self.name] = run_time

        if self.print:
            # just prints nicely
            print("--- time elapsed: {} = {:2f} s".format(self.name, run_time))


####################
### METHOD TIMER ###
####################
# EXPERIMENTAL

def log_time_function(func):
    """ decorator to log wall time of a function """
    @wraps(func)
    def perf_wrapper(*args, **kwargs):
        log_name = "{}.time".format(func.__qualname__)
        start_time = time.time()
        output = func(*args, **kwargs)
        run_time = time.time() - start_time

        log(logging.DEBUG, DataCategory.ONLY_PUBLIC_DATA, "--- time elapsed: {} = {:2f} s".format(log_name, run_time))
        log_metric(DataCategory.ONLY_PUBLIC_DATA, log_name, run_time)

        return output
    return perf_wrapper


def main():
    """ Test functions of this module """
    # try this script from command line only for testing
    # should never be executed otherwise

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # create formater with prefix
    stdout_handler = logging.StreamHandler(sys.stdout)
    systemlog_formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    stdout_handler.setFormatter(systemlog_formatter)
    logger.addHandler(stdout_handler)

    # create temp file for demo of metrics logging into file
    tmp_path = tempfile.NamedTemporaryFile(delete=False).name

    print("*** PURE OFFLINE MODE ***")

    # pure offline mode, no network access at all
    run = AmlRunWrapper()
    run.setup(output_file=tmp_path) # will write in this temp file any call to run

    run.log("accuracy", 0.5)
    run.log_row("epoch_report", epoch=15, accuracy=0.75)

    print("* After all this, here's the content of the output_file:")
    with open(tmp_path, "r") as ifile:
        print(ifile.read())

    print("*** GOING ONLINE ***")

    # azure ml connected Run (needs connectivity)
    run.setup(attach=True)
    run.log("accuracy", 0.365)
    run.log_row("epoch_report", epoch=22, accuracy=0.450)

    print("* After all this, here's the content of the output_file:")
    with open(tmp_path, "r") as ifile:
        print(ifile.read())

if __name__ == "__main__":
    main()

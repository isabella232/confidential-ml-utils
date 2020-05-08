"""
    AzureML Run wrapper for integration in user code
"""
import logging
import json

from .constants import DataCategory
from .log_utils import log

##################
### RUN OBJECT ###
##################

class AmlRunWrapper():
    """The purpose of this wrapper is to allow to import azureml.core.run
    only when "attached" from the module main function
    because we need to turn it off in detonation chamber
    """
    _recipe_azureml_run = None
    _metrics_file_path = None

    # https://python-patterns.guide/gang-of-four/singleton/
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AmlRunWrapper, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def setup(self, **kwargs):
        """Sets up based on keyword arguments

        Args:
            **kwargs (dict): keyword arguments

        Keyword Args:
            run (azureml.core.run.Run): if provided, use this run object to report metrics/logs
            attach (bool): attach to the current Run.get_context()
            output_file (str): path to a file for writing metric records in json
        """
        if kwargs.get('attach', False):
            log(logging.DEBUG, DataCategory.ONLY_PUBLIC_DATA, "Creating instance of azureml.core.run.Run")
            # IMPORTANT: keep this import outside of top level
            # because this requires aml connection
            from azureml.core.run import Run
            self._recipe_azureml_run = Run.get_context(allow_offline=True)
        elif 'run' in kwargs:
            self._recipe_azureml_run = kwargs.get('run')

        if 'output_file' in kwargs:
            self._metrics_file_path = kwargs.get('output_file')
            log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, "Will write metrics in {}".format(self._metrics_file_path))

    def __getattr__(self, name):
        """This is a very bad temporary hack of the Run class here.
        Whatever method from Run you'll call, it will forward to it.
        """
        def _transient_method(*args, **kwargs):
            log(logging.DEBUG, DataCategory.CONTAINS_PRIVATE_DATA, "Run.{}() called while offline, with args={} and kwargs={}".format(name, args, kwargs))
            if self._metrics_file_path:
                with open(self._metrics_file_path, "a") as ofile:
                    ofile.write(json.dumps({
                        "log_method": name,
                        "log_args": list(args),
                        "log_kwargs": kwargs
                    }))
                    ofile.write("\n")
            if self._recipe_azureml_run:
                func = getattr(self._recipe_azureml_run, name)
                func(*args, **kwargs)

        return _transient_method

def aml_run_attach():
    """ For calling from in user code """
    AmlRunWrapper().setup(attach=True)

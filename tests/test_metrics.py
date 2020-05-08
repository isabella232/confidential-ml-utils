import os
import sys
import tempfile

from . import context

from confidential_ml_utils.metrics import log_time_function
from confidential_ml_utils.metrics import log_time_block
from confidential_ml_utils.metrics import log_directory
from confidential_ml_utils.metrics import log_metric
from confidential_ml_utils.metrics import log_row
from confidential_ml_utils.run_wrapper import AmlRunWrapper
from confidential_ml_utils.constants import DataCategory

import time
from unittest.mock import Mock


def test_log_metric_public():
    aml_run_wrapper_mock = Mock()
    AmlRunWrapper._instance = aml_run_wrapper_mock  # replacing singleton

    run = AmlRunWrapper()
    assert isinstance(run, Mock)

    log_metric(
        DataCategory.ONLY_PUBLIC_DATA, # public data category
        "metric_key",
        3.14
    )
    aml_run_wrapper_mock.log.assert_called_once()
    aml_run_wrapper_mock.log_row.assert_not_called()
    aml_run_wrapper_mock.log.assert_called_with("metric_key", 3.14)


def test_log_metric_private():
    aml_run_wrapper_mock = Mock()
    AmlRunWrapper._instance = aml_run_wrapper_mock  # replacing singleton

    run = AmlRunWrapper()
    assert isinstance(run, Mock)

    log_metric(
        DataCategory.CONTAINS_PRIVATE_DATA, # public data category
        "metric_key",
        3.14
    )
    aml_run_wrapper_mock.log.assert_not_called()
    aml_run_wrapper_mock.log_row.assert_not_called()


def test_log_row_public():
    aml_run_wrapper_mock = Mock()
    AmlRunWrapper._instance = aml_run_wrapper_mock  # replacing singleton

    run = AmlRunWrapper()
    assert isinstance(run, Mock)

    log_row(
        DataCategory.ONLY_PUBLIC_DATA, # public data category
        "metric_row_key",
        foo=1.0,
        bar="text"
    )
    aml_run_wrapper_mock.log.assert_not_called()
    aml_run_wrapper_mock.log_row.assert_called_once()
    aml_run_wrapper_mock.log_row.assert_called_with("metric_row_key", foo=1.0, bar="text")


def test_log_row_private():
    aml_run_wrapper_mock = Mock()
    AmlRunWrapper._instance = aml_run_wrapper_mock  # replacing singleton

    run = AmlRunWrapper()
    assert isinstance(run, Mock)

    log_row(
        DataCategory.CONTAINS_PRIVATE_DATA, # public data category
        "metric_row_key",
        foo=1.0,
        bar="text"
    )
    aml_run_wrapper_mock.log.assert_not_called()
    aml_run_wrapper_mock.log_row.assert_not_called()

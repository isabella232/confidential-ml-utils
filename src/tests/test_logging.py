import confidential_ml_utils
import logging


def test_evil():
    logging.setLoggerClass(confidential_ml_utils.logging.ConfidentialLogger)
    log = logging.getLogger("name")
    log.debug("hi", category=confidential_ml_utils.constants.DataCategory.SENSITIVE)
    log.info("hi", category=confidential_ml_utils.constants.DataCategory.SENSITIVE)
    log.warning("hi", category=confidential_ml_utils.constants.DataCategory.SENSITIVE)

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import argparse
import confidential_ml_utils
from confidential_ml_utils.constants import DataCategory
import logging

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="SystemLog:")
    parser.add_argument("--log_level", default="INFO")
    args = parser.parse_args()

    confidential_ml_utils.enable_confidential_logging(
        args.prefix,
        level=args.log_level,
        format="%(prefix)s%(levelname)s:%(name)s:%(message)s",
    )

    # Output will be:
    # WARNING:30:private info
    # SystemLog:WARNING:30:public info
    logging.warning("private info")
    logging.warning("public info", category=DataCategory.PUBLIC)

    logger = logging.getLogger(__name__)

    # Output will be:
    # SystemLog:INFO:__main__:public info
    # SystemLog:WARNING:__main__:public info
    # WARNING:__main__:private info
    logger.info("public info", category=DataCategory.PUBLIC)
    logger.warning("public info", category=DataCategory.PUBLIC)
    logger.warning("private info")

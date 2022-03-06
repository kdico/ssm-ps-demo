__version__ = "0.1.0"

import json
import logging
import os
import platform
from importlib.metadata import version

logger = logging.getLogger()
logger.setLevel(logging.DEBUG if "DEBUG" in os.environ else logging.INFO)

logger.info("Python Version: {}".format(platform.python_version()))
logger.info(
    "Packages: {}".format(
        json.dumps(
            {name: version(name) for name in ("botocore", "boto3")}, indent=4
        )
    )
)

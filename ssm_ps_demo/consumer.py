__all__ = ["handler"]

import json
import os

import boto3

from ssm_ps_demo import logger

try:
    _STORE_FN_ARN = os.environ["STORE_FN_ARN"]
except KeyError:
    logger.exception("Store function ARN is required.")


def handler(*_) -> None:
    """Call the store function to get parameter values."""
    client = boto3.client("lambda")
    invoke_response = client.invoke(
        FunctionName=_STORE_FN_ARN,
        InvocationType="RequestResponse",
        Payload=json.dumps(["DB_HOST", "DB_PORT"]),
    )
    payload = invoke_response["Payload"]

    raw = payload.read()
    decoded = raw.decode("utf-8")
    parameters = json.loads(decoded)
    logger.info("Parameters: {}".format(json.dumps(parameters)))

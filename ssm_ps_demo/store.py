__all__ = ["handler"]

import collections
import json
import os

import boto3

from ssm_ps_demo import logger


class InvalidParametersError(Exception):
    """Exception thrown when a parameter is invalid."""

    def __init__(self, *parameters: str):
        self.message = "Invalid Parameters: {}".format(parameters)
        super().__init__(self.message)


class ParameterStore:
    """AWS SSM Parameter Store wrapper."""

    @staticmethod
    def get(*names: str) -> dict:
        """Calls AWS SSM Parameter Store to get parameter values.

        :param names: Parameter names.
        :return: A dictionary of parameter names and values.
        :raises InvalidParametersError: A parameter name is invalid.
        """
        client = boto3.client("ssm")
        try:
            logger.info("Getting Parameters: {}".format(names))
            response = client.get_parameters(
                Names=list(names), WithDecryption=_DECRYPTED
            )
            if len(response["InvalidParameters"]):
                raise InvalidParametersError(*response["InvalidParameters"])
            for parameter in response["Parameters"]:
                parameter["LastModifiedDate"] = (
                    parameter["LastModifiedDate"].timestamp() * 1000.0
                )
            logger.info(
                "Get Parameters Response: {}".format(
                    json.dumps(response, indent=4)
                )
            )
            return {
                parameter["Name"]: parameter["Value"]
                for parameter in response["Parameters"]
            }
        except client.exceptions.InvalidKeyId:
            logger.exception("The query key ID isn't valid.")
        except client.exceptions.InternalServerError:
            logger.exception("An error occurred on the server side.")
        except KeyError:
            logger.exception("SSM client response shape may have changed.")


class ParameterStoreCache(collections.UserDict):
    """Dictionary for caching parameter values."""

    def __missing__(self, key):
        if isinstance(key, str):
            raise KeyError(key)
        return self[str(key)]

    def __contains__(self, key):
        return str(key) in self.data

    def __setitem__(self, key, value):
        self.data[str(key)] = str(value)

    def read(self, *names: str) -> dict:
        """Read parameter values from cache. Calls the SSM Parameter Store
        for parameters not in cache and caches them.

        :param names: Parameter names.
        :return: Parameter values.
        """
        logger.info("Reading Parameters: {}".format(names))
        cached = {
            key: value for key, value in self.data.items() if key in names
        }
        # Requested parameter names that are not cached.
        missing = set(names) - (cached.keys() & names)
        if bool(missing):
            logger.info("Found parameter names not in cache.")
            pristine = ParameterStore.get(*missing)
            _cache.update(pristine)
            cached.update(pristine)
        return cached

    def expire(self) -> None:
        """Expires the cache."""
        logger.info("Clearing cache.")
        self.data.clear()


_DECRYPTED = "DECRYPT_PARAMS" in os.environ
_EXPIRE = "EXPIRE_CACHE" in os.environ

_cache = ParameterStoreCache()


def handler(names: list[str], _) -> str:
    """Get parameter values from AWS SSM Parameter Store
    if not already cached.

    :param names: Parameter names.
    :return: Parameter values.
    """
    if _EXPIRE is True:
        _cache.expire()
    parameters = _cache.read(*names)
    logger.info("Parameters: {}".format(json.dumps(parameters, indent=4)))
    return json.dumps(parameters)

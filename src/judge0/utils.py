"""Module containing different utility functions for Judge0 Python SDK."""

from collections.abc import Callable
from functools import wraps
from http import HTTPStatus
from typing import ParamSpec, TypeVar

from httpx import HTTPError, HTTPStatusError

from .errors import FreeTierCloudClientLimitError

P = ParamSpec("P")
R = TypeVar("R")


def is_http_too_many_requests_error(exception: Exception) -> bool:
    return (
        isinstance(exception, HTTPStatusError)
        and exception.response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    )


def handle_too_many_requests_error_for_free_tier_cloud_client(
    func: Callable[P, R],
) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except HTTPError as err:
            if is_http_too_many_requests_error(exception=err) and args:
                # If the raised exception is inside the one of the Judge0 Cloud clients
                # let's check if we are dealing with the implicit client.
                instance = args[0]
                class_name = instance.__class__.__name__
                # Check if we are using the free tier cloud client.
                if (
                    class_name in ("Judge0CloudCE", "Judge0CloudExtraCE")
                    and getattr(instance, "api_key", None) is None
                ):
                    raise FreeTierCloudClientLimitError(
                        "You are using the free tier cloud client and "
                        "you've hit a rate limit on it. Visit "
                        f"{getattr(instance, 'HOME_URL', None)} "
                        "to get your authentication credentials."
                    ) from err
            raise err from None

    return wrapper

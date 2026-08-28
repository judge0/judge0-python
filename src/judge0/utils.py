"""Module containing different utility functions for Judge0 Python SDK."""

import inspect
from collections.abc import Callable
from functools import wraps
from http import HTTPStatus
from typing import ParamSpec, TypeVar

from httpx import HTTPError, HTTPStatusError

from .errors import PreviewClientLimitError

P = ParamSpec("P")
R = TypeVar("R")

_PREVIEW_CLIENT_NAMES = (
    "Judge0CloudCE",
    "Judge0CloudExtraCE",
    "AsyncJudge0CloudCE",
    "AsyncJudge0CloudExtraCE",
)


def is_http_too_many_requests_error(exception: Exception) -> bool:
    return (
        isinstance(exception, HTTPStatusError)
        and exception.response.status_code == HTTPStatus.TOO_MANY_REQUESTS
    )


def _reraise_preview_limit_error(err: HTTPError, args: tuple[object, ...]) -> None:
    if is_http_too_many_requests_error(exception=err) and args:
        instance = args[0]
        class_name = instance.__class__.__name__
        if (
            class_name in _PREVIEW_CLIENT_NAMES
            and getattr(instance, "api_key", None) is None
        ):
            raise PreviewClientLimitError(
                "You are using a preview version of a client and "
                "you've hit a rate limit on it. Visit "
                f"{getattr(instance, 'HOME_URL', None)} "
                "to get your authentication credentials."
            ) from err
    raise err from None


def handle_too_many_requests_error_for_preview_client(
    func: Callable[P, R],
) -> Callable[P, R]:
    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)  # type: ignore[misc]
            except HTTPError as err:
                _reraise_preview_limit_error(err, args)
                raise

        return async_wrapper  # type: ignore[return-value]

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except HTTPError as err:
            _reraise_preview_limit_error(err, args)
            raise

    return wrapper

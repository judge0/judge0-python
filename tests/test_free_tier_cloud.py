from http import HTTPStatus

import httpx
import pytest

from judge0 import errors, utils
from judge0.errors import FreeTierCloudClientLimitError
from judge0.utils import handle_too_many_requests_error_for_free_tier_cloud_client


class Judge0CloudCE:
    HOME_URL = "https://ce.judge0.com"
    api_key = None

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def ping(self) -> None:
        request = httpx.Request("GET", "https://ce.judge0.com")
        response = httpx.Response(HTTPStatus.TOO_MANY_REQUESTS, request=request)
        raise httpx.HTTPStatusError(
            "rate limited",
            request=request,
            response=response,
        )


def test_preview_error_and_handler_names_are_removed() -> None:
    assert not hasattr(errors, "PreviewClientLimitError")
    assert not hasattr(utils, "handle_too_many_requests_error_for_preview_client")


def test_rate_limit_raises_free_tier_cloud_client_limit_error() -> None:
    with pytest.raises(
        FreeTierCloudClientLimitError,
        match="free tier cloud client",
    ):
        Judge0CloudCE().ping()

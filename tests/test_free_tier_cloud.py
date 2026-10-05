from http import HTTPStatus

import httpx2
import pytest

from judge0 import errors, utils
from judge0.errors import FreeTierCloudClientLimitError
from judge0.utils import handle_too_many_requests_error_for_free_tier_cloud_client


class Judge0CloudCE:
    HOME_URL = "https://ce.judge0.com"
    api_key: str | None = None

    @handle_too_many_requests_error_for_free_tier_cloud_client
    def ping(self, error: httpx2.HTTPError | None = None) -> None:
        if error is not None:
            raise error
        request = httpx2.Request("GET", "https://ce.judge0.com")
        response = httpx2.Response(HTTPStatus.TOO_MANY_REQUESTS, request=request)
        raise httpx2.HTTPStatusError(
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
    ) as exc_info:
        Judge0CloudCE().ping()

    assert isinstance(exc_info.value.__cause__, httpx2.HTTPStatusError)
    assert exc_info.value.__cause__.response.status_code == HTTPStatus.TOO_MANY_REQUESTS


@pytest.mark.parametrize(
    "status_code,expected",
    [(HTTPStatus.TOO_MANY_REQUESTS, True), (HTTPStatus.FORBIDDEN, False)],
)
def test_httpx2_rate_limit_detection(status_code: int, expected: bool) -> None:
    request = httpx2.Request("GET", Judge0CloudCE.HOME_URL)
    response = httpx2.Response(status_code, request=request)
    error = httpx2.HTTPStatusError("request failed", request=request, response=response)

    assert utils.is_http_too_many_requests_error(error) is expected


def test_authenticated_cloud_rate_limit_propagates_unchanged() -> None:
    client = Judge0CloudCE()
    client.api_key = "test-api-key"
    request = httpx2.Request("GET", client.HOME_URL)
    response = httpx2.Response(HTTPStatus.TOO_MANY_REQUESTS, request=request)
    error = httpx2.HTTPStatusError("rate limited", request=request, response=response)

    with pytest.raises(httpx2.HTTPStatusError) as exc_info:
        client.ping(error)

    assert exc_info.value is error


def test_other_http_errors_propagate_unchanged() -> None:
    request = httpx2.Request("GET", Judge0CloudCE.HOME_URL)
    response = httpx2.Response(HTTPStatus.INTERNAL_SERVER_ERROR, request=request)
    errors_to_check = [
        httpx2.HTTPStatusError("server error", request=request, response=response),
        httpx2.ConnectError("connection failed", request=request),
    ]

    for error in errors_to_check:
        assert not utils.is_http_too_many_requests_error(error)
        with pytest.raises(type(error)) as exc_info:
            Judge0CloudCE().ping(error)
        assert exc_info.value is error

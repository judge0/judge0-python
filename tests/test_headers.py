import pytest

from judge0 import Client
from judge0.version import __version__


@pytest.mark.parametrize(
    "client", ["judge0_cloud_ce_client", "judge0_cloud_extra_ce_client"]
)
def test_headers_presence(client: str, request: pytest.FixtureRequest) -> None:
    resolved_client: Client = request.getfixturevalue(client)

    assert "X-Judge0-App" in resolved_client.headers
    assert resolved_client.headers["X-Judge0-App"] == "Judge0 Python SDK"

    assert "X-Judge0-App-Version" in resolved_client.headers
    assert resolved_client.headers["X-Judge0-App-Version"] == __version__


@pytest.mark.parametrize("client", ["rapid_ce_client", "rapid_extra_ce_client"])
def test_headers_presence_with_existing_headers(
    client: str, request: pytest.FixtureRequest
) -> None:
    resolved_client: Client = request.getfixturevalue(client)

    assert "X-Judge0-App" in resolved_client.headers
    assert resolved_client.headers["X-Judge0-App"] == "Judge0 Python SDK"
    assert "x-rapidapi-host" in resolved_client.headers

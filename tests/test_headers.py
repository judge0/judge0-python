import pytest
from judge0.version import __version__


@pytest.mark.parametrize(
    "client", ["judge0_cloud_ce_client", "judge0_cloud_extra_ce_client"]
)
def test_headers_presence(client, request):
    client = request.getfixturevalue(client)

    assert "X-Judge0-App" in client.headers
    assert client.headers["X-Judge0-App"] == "Judge0 Python SDK"

    assert "X-Judge0-App-Version" in client.headers
    assert client.headers["X-Judge0-App-Version"] == __version__


@pytest.mark.parametrize("client", ["rapid_ce_client", "rapid_extra_ce_client"])
def test_headers_presence_with_existing_headers(client, request):
    client = request.getfixturevalue(client)

    assert "X-Judge0-App" in client.headers
    assert client.headers["X-Judge0-App"] == "Judge0 Python SDK"
    assert "x-rapidapi-host" in client.headers

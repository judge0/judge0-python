from judge0 import Client
from judge0.version import __version__


def _assert_sdk_headers(client: Client) -> None:
    assert client.headers["X-Judge0-App"] == "Judge0 Python SDK"
    assert client.headers["X-Judge0-App-Version"] == __version__


def test_headers_presence(cloud_client: Client) -> None:
    _assert_sdk_headers(cloud_client)


def test_headers_presence_with_existing_headers(rapid_client: Client) -> None:
    _assert_sdk_headers(rapid_client)
    assert "x-rapidapi-host" in rapid_client.headers

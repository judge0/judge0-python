import pytest

from judge0 import Client

DEFAULT_CLIENTS = (
    # "atd_ce_client",
    # "atd_extra_ce_client",
    "rapid_ce_client",
    "rapid_extra_ce_client",
    "judge0_cloud_ce_client",
    "judge0_cloud_extra_ce_client",
)


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_about(client: str, request: pytest.FixtureRequest) -> None:
    resolved_client: Client = request.getfixturevalue(client)
    resolved_client.get_about()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_config_info(client: str, request: pytest.FixtureRequest) -> None:
    resolved_client: Client = request.getfixturevalue(client)
    resolved_client.get_config_info()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_languages(client: str, request: pytest.FixtureRequest) -> None:
    resolved_client: Client = request.getfixturevalue(client)
    resolved_client.get_languages()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_statuses(client: str, request: pytest.FixtureRequest) -> None:
    resolved_client: Client = request.getfixturevalue(client)
    resolved_client.get_statuses()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_is_language_supported_multi_file_submission(
    client: str, request: pytest.FixtureRequest
) -> None:
    resolved_client: Client = request.getfixturevalue(client)
    assert resolved_client.is_language_supported(89)


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_is_language_supported_non_valid_lang_id(
    client: str, request: pytest.FixtureRequest
) -> None:
    resolved_client: Client = request.getfixturevalue(client)
    assert not resolved_client.is_language_supported(-1)

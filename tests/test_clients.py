import pytest

DEFAULT_CLIENTS = (
    "atd_ce_client",
    "atd_extra_ce_client",
    "rapid_ce_client",
    "rapid_extra_ce_client",
    "judge0_cloud_ce_client",
    "judge0_cloud_extra_ce_client",
)


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_about(client, request):
    client = request.getfixturevalue(client)
    client.get_about()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_config_info(client, request):
    client = request.getfixturevalue(client)
    client.get_config_info()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_languages(client, request):
    client = request.getfixturevalue(client)
    client.get_languages()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_get_statuses(client, request):
    client = request.getfixturevalue(client)
    client.get_statuses()


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_is_language_supported_multi_file_submission(client, request):
    client = request.getfixturevalue(client)
    assert client.is_language_supported(89)


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_is_language_supported_non_valid_lang_id(client, request):
    client = request.getfixturevalue(client)
    assert not client.is_language_supported(-1)

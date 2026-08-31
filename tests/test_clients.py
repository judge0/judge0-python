from judge0 import Client


def test_get_about(optional_client: Client) -> None:
    optional_client.get_about()


def test_get_config_info(optional_client: Client) -> None:
    optional_client.get_config_info()


def test_get_languages(optional_client: Client) -> None:
    optional_client.get_languages()


def test_get_statuses(optional_client: Client) -> None:
    optional_client.get_statuses()


def test_is_language_supported_multi_file_submission(optional_client: Client) -> None:
    assert optional_client.is_language_supported(89)


def test_is_language_supported_non_valid_lang_id(optional_client: Client) -> None:
    assert not optional_client.is_language_supported(-1)

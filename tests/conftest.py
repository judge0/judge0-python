import json
import os

import pytest
from dotenv import load_dotenv

from judge0 import clients, RegularPeriodRetry

load_dotenv()


@pytest.fixture(scope="session")
def custom_ce_client():
    endpoint = os.getenv("JUDGE0_CE_ENDPOINT")
    auth_headers = os.getenv("JUDGE0_CE_AUTH_HEADERS")

    if endpoint is None or auth_headers is None:
        return None
    else:
        return clients.Client(endpoint=endpoint, auth_headers=json.loads(auth_headers))


@pytest.fixture(scope="session")
def custom_extra_ce_client():
    endpoint = os.getenv("JUDGE0_EXTRA_CE_ENDPOINT")
    auth_headers = os.getenv("JUDGE0_EXTRA_CE_AUTH_HEADERS")

    if endpoint is None or auth_headers is None:
        return None
    else:
        return clients.Client(endpoint=endpoint, auth_headers=json.loads(auth_headers))


@pytest.fixture(scope="session")
def atd_ce_client():
    api_key = os.getenv("JUDGE0_ATD_API_KEY")

    if api_key is None:
        return None
    else:
        return clients.ATDJudge0CE(api_key)


@pytest.fixture(scope="session")
def atd_extra_ce_client():
    api_key = os.getenv("JUDGE0_ATD_API_KEY")

    if api_key is None:
        return None
    else:
        return clients.ATDJudge0ExtraCE(api_key)


@pytest.fixture(scope="session")
def rapid_ce_client():
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")

    if api_key is None:
        return None
    else:
        return clients.RapidJudge0CE(api_key)


@pytest.fixture(scope="session")
def rapid_extra_ce_client():
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")

    if api_key is None:
        return None
    else:
        return clients.RapidJudge0ExtraCE(api_key)


@pytest.fixture(scope="session")
def sulu_ce_client():
    api_key = os.getenv("JUDGE0_SULU_API_KEY")

    if api_key is None:
        return None
    else:
        return clients.SuluJudge0CE(api_key)


@pytest.fixture(scope="session")
def sulu_extra_ce_client():
    api_key = os.getenv("JUDGE0_SULU_API_KEY")

    if api_key is None:
        return None
    else:
        return clients.SuluJudge0ExtraCE(api_key)


@pytest.fixture(scope="session")
def preview_ce_client() -> clients.SuluJudge0CE:
    return clients.SuluJudge0CE(retry_strategy=RegularPeriodRetry(0.5))


@pytest.fixture(scope="session")
def preview_extra_ce_client() -> clients.SuluJudge0ExtraCE:
    return clients.SuluJudge0ExtraCE(retry_strategy=RegularPeriodRetry(0.5))


@pytest.fixture(scope="session")
def ce_client(
    custom_ce_client,
    sulu_ce_client,
    rapid_ce_client,
    atd_ce_client,
    preview_ce_client,
):
    if custom_ce_client is not None:
        return custom_ce_client
    if sulu_ce_client is not None:
        return sulu_ce_client
    if rapid_ce_client is not None:
        return rapid_ce_client
    if atd_ce_client is not None:
        return atd_ce_client
    if preview_ce_client is not None:
        return preview_ce_client

    pytest.fail("No CE client available for testing. This error should not happen!")


@pytest.fixture(scope="session")
def extra_ce_client(
    custom_extra_ce_client,
    sulu_extra_ce_client,
    rapid_extra_ce_client,
    atd_extra_ce_client,
    preview_extra_ce_client,
):
    if custom_extra_ce_client is not None:
        return custom_extra_ce_client
    if sulu_extra_ce_client is not None:
        return sulu_extra_ce_client
    if rapid_extra_ce_client is not None:
        return rapid_extra_ce_client
    if atd_extra_ce_client is not None:
        return atd_extra_ce_client
    if preview_extra_ce_client is not None:
        return preview_extra_ce_client

    pytest.fail(
        "No Extra CE client available for testing. This error should not happen!"
    )

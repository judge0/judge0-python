import json
import os

import pytest
from dotenv import load_dotenv

from judge0 import RegularPeriodRetry, clients

load_dotenv()


@pytest.fixture(scope="session")
def custom_ce_client() -> clients.Client | None:
    endpoint = os.getenv("JUDGE0_CE_ENDPOINT")
    auth_headers = os.getenv("JUDGE0_CE_AUTH_HEADERS")

    if endpoint is None or auth_headers is None:
        return None
    else:
        try:
            return clients.Client(endpoint=endpoint, headers=json.loads(auth_headers))
        except (json.JSONDecodeError, RuntimeError):
            return None


@pytest.fixture(scope="session")
def custom_extra_ce_client() -> clients.Client | None:
    endpoint = os.getenv("JUDGE0_EXTRA_CE_ENDPOINT")
    auth_headers = os.getenv("JUDGE0_EXTRA_CE_AUTH_HEADERS")

    if endpoint is None or auth_headers is None:
        return None
    else:
        try:
            return clients.Client(endpoint=endpoint, headers=json.loads(auth_headers))
        except (json.JSONDecodeError, RuntimeError):
            return None


@pytest.fixture(scope="session")
def atd_ce_client() -> clients.ATDJudge0CE | None:
    api_key = os.getenv("JUDGE0_ATD_API_KEY")

    if api_key is None:
        return None
    else:
        try:
            return clients.ATDJudge0CE(api_key)
        except RuntimeError:
            return None


@pytest.fixture(scope="session")
def atd_extra_ce_client() -> clients.ATDJudge0ExtraCE | None:
    api_key = os.getenv("JUDGE0_ATD_API_KEY")

    if api_key is None:
        return None
    else:
        try:
            return clients.ATDJudge0ExtraCE(api_key)
        except RuntimeError:
            return None


@pytest.fixture(scope="session")
def rapid_ce_client() -> clients.RapidJudge0CE | None:
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")

    if api_key is None:
        return None
    else:
        try:
            return clients.RapidJudge0CE(api_key)
        except RuntimeError:
            return None


@pytest.fixture(scope="session")
def rapid_extra_ce_client() -> clients.RapidJudge0ExtraCE | None:
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")

    if api_key is None:
        return None
    else:
        try:
            return clients.RapidJudge0ExtraCE(api_key)
        except RuntimeError:
            return None


@pytest.fixture(scope="session")
def judge0_cloud_ce_client() -> clients.Judge0CloudCE | None:
    auth_headers = os.getenv("JUDGE0_CLOUD_CE_AUTH_HEADERS")

    if auth_headers is None:
        return None
    else:
        try:
            return clients.Judge0CloudCE(auth_headers)
        except RuntimeError:
            return None


@pytest.fixture(scope="session")
def judge0_cloud_extra_ce_client() -> clients.Judge0CloudExtraCE | None:
    auth_headers = os.getenv("JUDGE0_CLOUD_EXTRA_CE_AUTH_HEADERS")

    if auth_headers is None:
        return None
    else:
        try:
            return clients.Judge0CloudExtraCE(auth_headers)
        except RuntimeError:
            return None


@pytest.fixture(scope="session")
def free_tier_cloud_ce_client() -> clients.Judge0CloudCE:
    return clients.Judge0CloudCE(retry_strategy=RegularPeriodRetry(0.5))


@pytest.fixture(scope="session")
def free_tier_cloud_extra_ce_client() -> clients.Judge0CloudExtraCE:
    return clients.Judge0CloudExtraCE(retry_strategy=RegularPeriodRetry(0.5))


@pytest.fixture(scope="session")
def ce_client(
    custom_ce_client: clients.Client | None,
    judge0_cloud_ce_client: clients.Judge0CloudCE | None,
    rapid_ce_client: clients.RapidJudge0CE | None,
    # atd_ce_client,
    free_tier_cloud_ce_client: clients.Judge0CloudCE,
) -> clients.Client:
    if custom_ce_client is not None:
        return custom_ce_client
    if judge0_cloud_ce_client is not None:
        return judge0_cloud_ce_client
    if rapid_ce_client is not None:
        return rapid_ce_client
    # if atd_ce_client is not None:
    #     return atd_ce_client
    if free_tier_cloud_ce_client is not None:
        return free_tier_cloud_ce_client

    pytest.fail("No CE client available for testing. This error should not happen!")


@pytest.fixture(scope="session")
def extra_ce_client(
    custom_extra_ce_client: clients.Client | None,
    judge0_cloud_extra_ce_client: clients.Judge0CloudExtraCE | None,
    rapid_extra_ce_client: clients.RapidJudge0ExtraCE | None,
    # atd_extra_ce_client,
    free_tier_cloud_extra_ce_client: clients.Judge0CloudExtraCE,
) -> clients.Client:
    if custom_extra_ce_client is not None:
        return custom_extra_ce_client
    if judge0_cloud_extra_ce_client is not None:
        return judge0_cloud_extra_ce_client
    if rapid_extra_ce_client is not None:
        return rapid_extra_ce_client
    # if atd_extra_ce_client is not None:
    #     return atd_extra_ce_client
    if free_tier_cloud_extra_ce_client is not None:
        return free_tier_cloud_extra_ce_client

    pytest.fail(
        "No Extra CE client available for testing. This error should not happen!"
    )

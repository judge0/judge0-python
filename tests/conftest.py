import json
import os
from collections.abc import Callable
from typing import TypeVar

import pytest
from dotenv import load_dotenv

from judge0 import RegularPeriodRetry, clients

load_dotenv()

TClient = TypeVar("TClient", bound=clients.Client)

# ATD fixtures remain available but are not part of the default live matrix.
DEFAULT_CLIENT_FIXTURES = (
    "rapid_ce_client",
    "rapid_extra_ce_client",
    "judge0_cloud_ce_client",
    "judge0_cloud_extra_ce_client",
)
CLOUD_CLIENT_FIXTURES = (
    "judge0_cloud_ce_client",
    "judge0_cloud_extra_ce_client",
)
RAPID_CLIENT_FIXTURES = (
    "rapid_ce_client",
    "rapid_extra_ce_client",
)


def _try_create_client(factory: Callable[[], TClient]) -> TClient | None:
    try:
        return factory()
    except (json.JSONDecodeError, RuntimeError):
        return None


def _require_named_client(request: pytest.FixtureRequest) -> clients.Client:
    client = request.getfixturevalue(request.param)
    if client is None:
        pytest.skip(f"{request.param} is not configured")
    return client


def _first_available_client(*candidates: clients.Client | None) -> clients.Client:
    for client in candidates:
        if client is not None:
            return client
    pytest.fail("No client available for testing. This error should not happen!")


@pytest.fixture(scope="session")
def custom_ce_client() -> clients.Client | None:
    endpoint = os.getenv("JUDGE0_CE_ENDPOINT")
    auth_headers = os.getenv("JUDGE0_CE_AUTH_HEADERS")
    if endpoint is None or auth_headers is None:
        return None
    return _try_create_client(
        lambda: clients.Client(endpoint=endpoint, headers=json.loads(auth_headers))
    )


@pytest.fixture(scope="session")
def custom_extra_ce_client() -> clients.Client | None:
    endpoint = os.getenv("JUDGE0_EXTRA_CE_ENDPOINT")
    auth_headers = os.getenv("JUDGE0_EXTRA_CE_AUTH_HEADERS")
    if endpoint is None or auth_headers is None:
        return None
    return _try_create_client(
        lambda: clients.Client(endpoint=endpoint, headers=json.loads(auth_headers))
    )


@pytest.fixture(scope="session")
def atd_ce_client() -> clients.ATDJudge0CE | None:
    api_key = os.getenv("JUDGE0_ATD_API_KEY")
    if api_key is None:
        return None
    return _try_create_client(lambda: clients.ATDJudge0CE(api_key))


@pytest.fixture(scope="session")
def atd_extra_ce_client() -> clients.ATDJudge0ExtraCE | None:
    api_key = os.getenv("JUDGE0_ATD_API_KEY")
    if api_key is None:
        return None
    return _try_create_client(lambda: clients.ATDJudge0ExtraCE(api_key))


@pytest.fixture(scope="session")
def rapid_ce_client() -> clients.RapidJudge0CE | None:
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")
    if api_key is None:
        return None
    return _try_create_client(lambda: clients.RapidJudge0CE(api_key))


@pytest.fixture(scope="session")
def rapid_extra_ce_client() -> clients.RapidJudge0ExtraCE | None:
    api_key = os.getenv("JUDGE0_RAPID_API_KEY")
    if api_key is None:
        return None
    return _try_create_client(lambda: clients.RapidJudge0ExtraCE(api_key))


@pytest.fixture(scope="session")
def judge0_cloud_ce_client() -> clients.Judge0CloudCE | None:
    auth_headers = os.getenv("JUDGE0_CLOUD_CE_AUTH_HEADERS")
    if auth_headers is None:
        return None
    return _try_create_client(lambda: clients.Judge0CloudCE(auth_headers))


@pytest.fixture(scope="session")
def judge0_cloud_extra_ce_client() -> clients.Judge0CloudExtraCE | None:
    auth_headers = os.getenv("JUDGE0_CLOUD_EXTRA_CE_AUTH_HEADERS")
    if auth_headers is None:
        return None
    return _try_create_client(lambda: clients.Judge0CloudExtraCE(auth_headers))


@pytest.fixture(scope="session")
def preview_ce_client() -> clients.Judge0CloudCE:
    return clients.Judge0CloudCE(retry_strategy=RegularPeriodRetry(0.5))


@pytest.fixture(scope="session")
def preview_extra_ce_client() -> clients.Judge0CloudExtraCE:
    return clients.Judge0CloudExtraCE(retry_strategy=RegularPeriodRetry(0.5))


@pytest.fixture(scope="session")
def ce_client(
    custom_ce_client: clients.Client | None,
    judge0_cloud_ce_client: clients.Judge0CloudCE | None,
    rapid_ce_client: clients.RapidJudge0CE | None,
    preview_ce_client: clients.Judge0CloudCE,
) -> clients.Client:
    return _first_available_client(
        custom_ce_client,
        judge0_cloud_ce_client,
        rapid_ce_client,
        preview_ce_client,
    )


@pytest.fixture(scope="session")
def extra_ce_client(
    custom_extra_ce_client: clients.Client | None,
    judge0_cloud_extra_ce_client: clients.Judge0CloudExtraCE | None,
    rapid_extra_ce_client: clients.RapidJudge0ExtraCE | None,
    preview_extra_ce_client: clients.Judge0CloudExtraCE,
) -> clients.Client:
    return _first_available_client(
        custom_extra_ce_client,
        judge0_cloud_extra_ce_client,
        rapid_extra_ce_client,
        preview_extra_ce_client,
    )


@pytest.fixture(scope="session", params=DEFAULT_CLIENT_FIXTURES, ids=lambda name: name)
def optional_client(request: pytest.FixtureRequest) -> clients.Client:
    return _require_named_client(request)


@pytest.fixture(scope="session", params=CLOUD_CLIENT_FIXTURES, ids=lambda name: name)
def cloud_client(request: pytest.FixtureRequest) -> clients.Client:
    return _require_named_client(request)


@pytest.fixture(scope="session", params=RAPID_CLIENT_FIXTURES, ids=lambda name: name)
def rapid_client(request: pytest.FixtureRequest) -> clients.Client:
    return _require_named_client(request)

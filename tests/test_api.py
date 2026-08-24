from typing import cast

import pytest

import judge0
from judge0 import Flavor, LanguageAlias, Submission, get_client
from judge0.api import _resolve_client


def test_resolve_client_with_explicit_client(optional_client: judge0.Client) -> None:
    assert _resolve_client(optional_client) is optional_client


@pytest.mark.parametrize(
    "flavor,expected_client",
    [
        (Flavor.CE, "JUDGE0_IMPLICIT_CE_CLIENT"),
        (Flavor.EXTRA_CE, "JUDGE0_IMPLICIT_EXTRA_CE_CLIENT"),
    ],
)
def test_resolve_client_with_flavor(
    flavor: Flavor,
    expected_client: str,
) -> None:
    # Implicit clients start as None and are set on first resolution.
    assert _resolve_client(client=flavor) is getattr(judge0, expected_client)


@pytest.mark.parametrize("submissions", [[], None])
def test_resolve_client_empty_submissions_argument(
    submissions: list[Submission] | None,
) -> None:
    with pytest.raises(ValueError):
        _resolve_client(submissions=submissions)


def test_get_client_rejects_invalid_flavor_type() -> None:
    with pytest.raises(TypeError, match="Flavor"):
        get_client(cast(Flavor, "CE"))


def test_resolve_client_no_common_client_for_submissions() -> None:
    submissions = [
        Submission(source_code="", language=LanguageAlias.CPP_GCC),
        Submission(source_code="", language=LanguageAlias.PYTHON_FOR_ML),
    ]

    with pytest.raises(RuntimeError):
        _resolve_client(submissions=submissions)


def test_resolve_client_common_ce_client() -> None:
    submissions = [
        Submission(source_code="", language=LanguageAlias.CPP_GCC),
        Submission(source_code="", language=LanguageAlias.PYTHON),
    ]

    assert _resolve_client(submissions=submissions) is judge0.JUDGE0_IMPLICIT_CE_CLIENT


def test_resolve_client_common_extra_ce_client() -> None:
    submissions = [
        Submission(source_code="", language=LanguageAlias.CPP_CLANG),
        Submission(source_code="", language=LanguageAlias.PYTHON_FOR_ML),
    ]

    assert (
        _resolve_client(submissions=submissions)
        is judge0.JUDGE0_IMPLICIT_EXTRA_CE_CLIENT
    )

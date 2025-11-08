import judge0
import pytest

from judge0 import Flavor, LanguageAlias, Submission
from judge0.api import _resolve_client

DEFAULT_CLIENTS = (
    "atd_ce_client",
    "atd_extra_ce_client",
    "rapid_ce_client",
    "rapid_extra_ce_client",
    "judge0_cloud_ce_client",
    "judge0_cloud_extra_ce_client",
)


@pytest.mark.parametrize("client", DEFAULT_CLIENTS)
def test_resolve_client_with_explicit_client(client, request):
    client = request.getfixturevalue(client)
    assert _resolve_client(client) is client


@pytest.mark.parametrize(
    "flavor,expected_client",
    [
        [
            Flavor.CE,
            "JUDGE0_IMPLICIT_CE_CLIENT",
        ],
        [
            Flavor.EXTRA_CE,
            "JUDGE0_IMPLICIT_EXTRA_CE_CLIENT",
        ],
    ],
)
def test_resolve_client_with_flavor(
    flavor,
    expected_client,
):
    # We have to use getattr since both implicit clients are initially None.
    assert _resolve_client(client=flavor) is getattr(judge0, expected_client)


@pytest.mark.parametrize(
    "submissions",
    [
        [],
        None,
    ],
)
def test_resolve_client_empty_submissions_argument(submissions):
    with pytest.raises(ValueError):
        _resolve_client(submissions=submissions)


def test_resolve_client_no_common_client_for_submissions():
    cpp_submission = Submission(
        source_code="",  # source code is not important in this test
        language=LanguageAlias.CPP_GCC,
    )

    py_submission = Submission(
        source_code="",  # source code is not important in this test
        language=LanguageAlias.PYTHON_FOR_ML,
    )

    submissions = [cpp_submission, py_submission]

    with pytest.raises(RuntimeError):
        _resolve_client(submissions=submissions)


def test_resolve_client_common_ce_client():
    cpp_submission = Submission(
        source_code="",  # source code is not important in this test
        language=LanguageAlias.CPP_GCC,
    )

    py_submission = Submission(
        source_code="",  # source code is not important in this test
        language=LanguageAlias.PYTHON,
    )

    submissions = [cpp_submission, py_submission]

    assert _resolve_client(submissions=submissions) is judge0.JUDGE0_IMPLICIT_CE_CLIENT


def test_resolve_client_common_extra_ce_client():
    cpp_submission = Submission(
        source_code="",  # source code is not important in this test
        language=LanguageAlias.CPP_CLANG,
    )

    py_submission = Submission(
        source_code="",  # source code is not important in this test
        language=LanguageAlias.PYTHON_FOR_ML,
    )

    submissions = [cpp_submission, py_submission]

    assert (
        _resolve_client(submissions=submissions)
        is judge0.JUDGE0_IMPLICIT_EXTRA_CE_CLIENT
    )

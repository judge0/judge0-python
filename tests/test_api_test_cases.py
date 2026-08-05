"""Separate file containing tests related to test case functionality."""

from typing import Any

import pytest

import judge0
from judge0.api import create_submissions_from_test_cases
from judge0.base_types import LanguageAlias, Status, TestCase, TestCaseType
from judge0.submission import Submission


@pytest.mark.parametrize(
    "test_case,expected_output",
    [
        [
            TestCase(input="input_1", expected_output="output_1"),
            TestCase(input="input_1", expected_output="output_1"),
        ],
        [
            (),
            TestCase(input=None, expected_output=None),
        ],
        [
            ("input_tuple",),
            TestCase(input="input_tuple", expected_output=None),
        ],
        [
            ("input_tuple", "output_tuple"),
            TestCase(input="input_tuple", expected_output="output_tuple"),
        ],
        [
            [],
            TestCase(input=None, expected_output=None),
        ],
        [
            ["input_list"],
            TestCase(input="input_list", expected_output=None),
        ],
        [
            ["input_list", "output_list"],
            TestCase(input="input_list", expected_output="output_list"),
        ],
        [
            {"input": "input_dict", "expected_output": "output_dict"},
            TestCase(input="input_dict", expected_output="output_dict"),
        ],
        [
            None,
            None,
        ],
    ],
)
def test_test_case_from_record(
    test_case: TestCaseType | None, expected_output: TestCase | None
) -> None:
    assert TestCase.from_record(test_case) == expected_output


@pytest.mark.parametrize(
    "submissions,test_cases,expected_type",
    [
        [Submission(source_code=""), TestCase(), Submission],
        [[Submission(source_code="")], TestCase(), list],
        [Submission(source_code=""), [TestCase()], list],
        [[Submission(source_code="")], [TestCase()], list],
    ],
)
def test_create_submissions_from_test_cases_return_type(
    submissions: Submission | list[Submission],
    test_cases: TestCase | list[TestCase],
    expected_type: type[Any],
) -> None:
    output = create_submissions_from_test_cases(submissions, test_cases)
    assert type(output) is expected_type


class TestCreateSubmissionsFromTestCases:
    @pytest.mark.parametrize(
        "test_case,stdin,expected_output",
        [
            [TestCase(), None, None],
            [[], None, None],
            [{}, None, None],
            [(), None, None],
        ],
    )
    def test_empty_test_case(
        self,
        test_case: TestCaseType,
        stdin: str | None,
        expected_output: str | None,
    ) -> None:
        submission = create_submissions_from_test_cases(
            Submission(), test_cases=test_case
        )

        assert (
            submission.stdin == stdin and submission.expected_output == expected_output
        )

    @pytest.mark.parametrize(
        "test_case,stdin,expected_output",
        [
            [TestCase(), None, None],
            [TestCase(input="input"), "input", None],
            [TestCase(expected_output="output"), None, "output"],
            [["input_list"], "input_list", None],
            [["input_list", "output_list"], "input_list", "output_list"],
            [{"input": "input_dict"}, "input_dict", None],
            [
                {"input": "input_dict", "expected_output": "output_dict"},
                "input_dict",
                "output_dict",
            ],
            [("input_tuple",), "input_tuple", None],
            [("input_tuple", "output_tuple"), "input_tuple", "output_tuple"],
        ],
    )
    def test_single_test_case(
        self,
        test_case: TestCaseType,
        stdin: str | None,
        expected_output: str | None,
    ) -> None:
        submission = create_submissions_from_test_cases(
            Submission(), test_cases=test_case
        )

        assert (
            submission.stdin == stdin and submission.expected_output == expected_output
        )

    @pytest.mark.parametrize(
        "test_cases,stdin,expected_output",
        [
            [[TestCase()], None, None],
            [[TestCase(input="input")], "input", None],
            [[TestCase(expected_output="output")], None, "output"],
            [(["input_list"],), "input_list", None],
            [(["input_list", "output_list"],), "input_list", "output_list"],
            [({"input": "input_dict"},), "input_dict", None],
            [
                ({"input": "input_dict", "expected_output": "output_dict"},),
                "input_dict",
                "output_dict",
            ],
            [
                [
                    ("input_tuple",),
                ],
                "input_tuple",
                None,
            ],
            [
                [
                    ("input_tuple", "output_tuple"),
                ],
                "input_tuple",
                "output_tuple",
            ],
        ],
    )
    def test_single_test_case_in_iterable(
        self,
        test_cases: list[TestCaseType] | tuple[TestCaseType, ...],
        stdin: str | None,
        expected_output: str | None,
    ) -> None:
        submissions = create_submissions_from_test_cases(
            Submission(), test_cases=test_cases
        )

        for submission in submissions:
            assert (
                submission.stdin == stdin
                and submission.expected_output == expected_output
            )


@pytest.mark.parametrize(
    "source_code_or_submissions,test_cases,expected_status",
    [
        [
            "print(f'Hello, {input()}')",
            [TestCase("Judge0", "Hello, Judge0")],
            [Status.ACCEPTED],
        ],
        [
            "print(f'Hello, {input()}')",
            [
                TestCase("Judge0", "Hello, Judge0"),
                TestCase("pytest", "Hello, pytest"),
            ],
            [Status.ACCEPTED, Status.ACCEPTED],
        ],
        [
            Submission(
                source_code="print(f'Hello, {input()}')",
                language=LanguageAlias.PYTHON,
            ),
            [
                TestCase("Judge0", "Hello, Judge0"),
            ],
            [Status.ACCEPTED],
        ],
        [
            Submission(
                source_code="print(f'Hello, {input()}')",
                language=LanguageAlias.PYTHON,
            ),
            [
                TestCase("Judge0", "Hello, Judge0"),
                TestCase("pytest", "Hi, pytest"),
            ],
            [Status.ACCEPTED, Status.WRONG_ANSWER],
        ],
        [
            [
                Submission(
                    source_code="print(f'Hello, {input()}')",
                    language=LanguageAlias.PYTHON,
                ),
                Submission(
                    source_code="print(f'Hello,  {input()}')",
                    language=LanguageAlias.PYTHON,
                ),
            ],
            [
                TestCase("Judge0", "Hello, Judge0"),
                TestCase("pytest", "Hello, pytest"),
            ],
            [
                Status.ACCEPTED,
                Status.ACCEPTED,
                Status.WRONG_ANSWER,
                Status.WRONG_ANSWER,
            ],
        ],
    ],
)
def test_test_cases_from_run(
    source_code_or_submissions: str | Submission | list[Submission],
    test_cases: list[TestCase],
    expected_status: list[Status],
    request: pytest.FixtureRequest,
) -> None:
    client: judge0.Client = request.getfixturevalue("ce_client")

    if isinstance(source_code_or_submissions, str):
        submissions = judge0.run(
            client=client,
            source_code=source_code_or_submissions,
            test_cases=test_cases,
            language=LanguageAlias.PYTHON,
        )
    else:
        submissions = judge0.run(
            client=client,
            submissions=source_code_or_submissions,
            test_cases=test_cases,
        )

    assert [submission.status for submission in submissions] == expected_status


@pytest.mark.parametrize(
    "submissions,expected_status",
    [
        [
            Submission(
                source_code="print(f'Hello, {input()}')",
                language=LanguageAlias.PYTHON,
                stdin="Judge0",
                expected_output="Hello, Judge0",
            ),
            Status.ACCEPTED,
        ],
        [
            [
                Submission(
                    source_code="print(f'Hello, {input()}')",
                    language=LanguageAlias.PYTHON,
                    stdin="Judge0",
                    expected_output="Hello, Judge0",
                ),
                Submission(
                    source_code="print(f'Hello, {input()}')",
                    language=LanguageAlias.PYTHON,
                    stdin="pytest",
                    expected_output="Hello, pytest",
                ),
            ],
            [Status.ACCEPTED, Status.ACCEPTED],
        ],
    ],
)
def test_no_test_cases(
    submissions: Submission | list[Submission],
    expected_status: Status | list[Status],
    request: pytest.FixtureRequest,
) -> None:
    client: judge0.Client = request.getfixturevalue("ce_client")

    results = judge0.run(
        client=client,
        submissions=submissions,
    )

    if isinstance(results, Submission):
        assert results.status == expected_status
    else:
        assert [submission.status for submission in results] == expected_status


@pytest.mark.parametrize("n_submissions", [42, 84])
def test_batched_test_cases(n_submissions: int, request: pytest.FixtureRequest) -> None:
    client: judge0.Client = request.getfixturevalue("ce_client")
    submissions = [
        Submission(
            source_code=f"print({i})",
            language=LanguageAlias.PYTHON,
            expected_output=f"{i}",
        )
        for i in range(n_submissions)
    ]

    results = judge0.run(client=client, submissions=submissions)

    assert len(results) == n_submissions
    assert all(result.status == Status.ACCEPTED for result in results)

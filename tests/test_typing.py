from typing import TYPE_CHECKING, cast

from typing_extensions import assert_type

from judge0 import Client, Submission, TestCase, async_execute, run
from judge0.api import create_submissions, get_submissions, wait
from judge0.submission import Submissions

if TYPE_CHECKING:
    client = cast(Client, object())
    submission = Submission(source_code="print('hello')")
    submissions = [submission]

    assert_type(create_submissions(client=client, submissions=submission), Submission)
    assert_type(create_submissions(client=client, submissions=submissions), Submissions)
    assert_type(get_submissions(client=client, submissions=submission), Submission)
    assert_type(get_submissions(client=client, submissions=submissions), Submissions)
    assert_type(wait(client=client, submissions=submission), Submission)
    assert_type(wait(client=client, submissions=submissions), Submissions)

    assert_type(async_execute(client=client, source_code="print('hello')"), Submission)
    assert_type(async_execute(client=client, source_code=b"executable"), Submission)
    assert_type(async_execute(client=client, submissions=submission), Submission)
    assert_type(async_execute(client=client, submissions=submissions), Submissions)
    assert_type(
        async_execute(
            client=client,
            source_code="print('hello')",
            test_cases=[TestCase()],
        ),
        list[Submission],
    )

    assert_type(run(client=client, source_code="print('hello')"), Submission)
    assert_type(run(client=client, source_code=b"executable"), Submission)
    assert_type(run(client=client, submissions=submission), Submission)
    assert_type(run(client=client, submissions=submissions), Submissions)

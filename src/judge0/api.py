from typing import Optional, Union
from collections.abc import Iterable

from .clients import Client
from .common import Flavor
from .retry import RegularPeriodRetry, RetryMechanism
from .submission import Submission


def resolve_client(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
) -> Union[Client, None]:
    # User explicitly passed a client.
    if isinstance(client, Client):
        return client

    from . import _get_implicit_client

    # User explicitly choose the flavor of the client.
    if isinstance(client, Flavor):
        return _get_implicit_client(flavor=client)

    if client is None and isinstance(submissions, list) and len(submissions) == 0:
        raise ValueError("Client cannot be determined from empty submissions.")

    # client is None and we have to determine a flavor of the client from the
    # submissions and the languages.
    if isinstance(submissions, Submission):
        submissions = [submissions]

    # Check which client supports all languages from the provided submissions.
    languages = [submission.language_id for submission in submissions]

    for flavor in Flavor:
        client = _get_implicit_client(flavor)
        if client is not None and all(
            (client.is_language_supported(lang) for lang in languages)
        ):
            return client

    raise RuntimeError(
        "Failed to resolve the client from submissions argument. "
        "None of the implicit clients supports all languages from the submissions. "
        "Please explicitly provide the client argument."
    )


def create_submissions(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Union[Submission, list[Submission]] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client=client, submissions=submissions)

    MAX_SUBMISSION_BATCH_SIZE = (
        20  # TODO: move to client.config.MAX_SUBMISSION_BATCH_SIZE
    )
    ENABLE_BATCHED_SUBMISSIONS = (
        True  # TODO: Move to client.config.ENABLE_BATCHED_SUBMISSIONS
    )
    actual_batch_size = (
        MAX_SUBMISSION_BATCH_SIZE if ENABLE_BATCHED_SUBMISSIONS else 1
    )  # TODO: Move to client.config.BATCH_SIZE which should be calculated field

    if isinstance(submissions, (list, tuple)):
        if len(submissions) == 0:
            return submissions
        elif len(submissions) == 1:
            return [client.create_submission(submissions[0])]
        else:
            if actual_batch_size > 1:
                submissions_left = client.create_submissions(
                    submissions=submissions[:actual_batch_size]
                )
            else:
                submissions_left = client.create_submission(submissions[0])

            if not isinstance(submissions_left, list):
                submissions_left = [submissions_left]

            submissions_right = create_submissions(
                client=client, submissions=submissions[actual_batch_size:]
            )
            if not isinstance(submissions_right, list):
                submissions_right = [submissions_right]

            return [*submissions_left, *submissions_right]
    else:
        return client.create_submission(submissions)


def get_submissions(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Union[Submission, list[Submission]] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client=client, submissions=submissions)

    MAX_SUBMISSION_BATCH_SIZE = (
        20  # TODO: move to client.config.MAX_SUBMISSION_BATCH_SIZE
    )
    ENABLE_BATCHED_SUBMISSIONS = (
        True  # TODO: Move to client.config.ENABLE_BATCHED_SUBMISSIONS
    )
    actual_batch_size = (
        MAX_SUBMISSION_BATCH_SIZE if ENABLE_BATCHED_SUBMISSIONS else 1
    )  # TODO: Move to client.config.BATCH_SIZE which should be calculated field

    if isinstance(submissions, (list, tuple)):
        if len(submissions) == 0:
            return submissions
        elif len(submissions) == 1:
            return [client.get_submission(submissions[0])]
        else:
            if actual_batch_size > 1:
                submissions_left = client.get_submissions(
                    submissions=submissions[:actual_batch_size]
                )
            else:
                submissions_left = client.get_submission(submissions[0])

            if not isinstance(submissions_left, list):
                submissions_left = [submissions_left]

            submissions_right = get_submissions(
                client=client, submissions=submissions[actual_batch_size:]
            )
            if not isinstance(submissions_right, list):
                submissions_right = [submissions_right]

            return [*submissions_left, *submissions_right]
    else:
        return client.get_submission(submissions)


def wait(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Union[Submission, list[Submission]] = None,
    retry_mechanism: Optional[RetryMechanism] = None,
) -> Union[Submission, list[Submission]]:
    client = resolve_client(client=client, submissions=submissions)

    if retry_mechanism is None:
        retry_mechanism = RegularPeriodRetry()

    if isinstance(submissions, (list, tuple)):
        submissions_to_check = {
            submission.token: submission for submission in submissions
        }
    else:
        submissions_to_check = {
            submission.token: submission for submission in [submissions]
        }

    while len(submissions_to_check) > 0 and not retry_mechanism.is_done():
        # TODO: list should not be needed if use collections.abc.Iterable for isinstance check.
        get_submissions(client=client, submissions=list(submissions_to_check.values()))
        for token in list(submissions_to_check):
            submission = submissions_to_check[token]
            if submission.is_done():
                submissions_to_check.pop(token)

        # Don't wait if there is no submissions to check for anymore.
        if len(submissions_to_check) == 0:
            break

        retry_mechanism.wait()
        retry_mechanism.step()

    return submissions


def _execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    wait_for_result: bool = False,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    if submissions is not None and source_code is not None:
        raise ValueError(
            "Both submissions and source_code arguments are provided. "
            "Provide only one of the two."
        )
    if submissions is None and source_code is None:
        raise ValueError("Neither source_code nor submissions argument are provided.")

    if source_code is not None:
        submissions = Submission(source_code=source_code, **kwargs)

    client = resolve_client(client=client, submissions=submissions)
    submissions = create_submissions(client=client, submissions=submissions)

    if wait_for_result:
        return wait(client=client, submissions=submissions)
    else:
        return submissions


def async_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=False,
        **kwargs,
    )


def sync_execute(
    *,
    client: Optional[Union[Client, Flavor]] = None,
    submissions: Optional[Union[Submission, list[Submission]]] = None,
    source_code: Optional[str] = None,
    **kwargs,
) -> Union[Submission, list[Submission]]:
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=True,
        **kwargs,
    )


execute = sync_execute
run = execute
async_run = async_execute

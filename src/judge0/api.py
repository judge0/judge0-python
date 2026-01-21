import logging

from .base_types import Flavor, Iterable, TestCase, TestCases, TestCaseType
from .clients import Client
from .common import batched
from .errors import ClientResolutionError
from .retry import RegularPeriodRetry, RetryStrategy
from .submission import Submission, Submissions

logger = logging.getLogger(__name__)


def get_client(flavor: Flavor = Flavor.CE) -> Client:
    """Resolve client from API keys from environment or default to preview client.

    Parameters
    ----------
    flavor : Flavor
        Flavor of Judge0 Client.

    Returns
    -------
    Client
        An object of base type Client and the specified flavor.
    """
    from . import _get_implicit_client

    if isinstance(flavor, Flavor):
        client = _get_implicit_client(flavor=flavor)
        logger.debug(f"Resolved implicit client for flavor {flavor}: {client}")
        return client
    else:
        raise ValueError(
            "Expected argument flavor to be of of type enum Flavor, "
            f"got {type(flavor)}."
        )


def _resolve_client(
    client: Client | Flavor | None = None,
    submissions: Submission | Submissions | None = None,
) -> Client:
    """Resolve a client from flavor or submission(s) arguments.

    Parameters
    ----------
    client : Client or Flavor, optional
        A Client object or flavor of client. Returns the client if not None.
    submissions: Submission or Submissions, optional
        Submission(s) used to determine the suitable client.

    Returns
    -------
    Client
        An object of base type Client.

    Raises
    ------
    ClientResolutionError
        If there is no implemented client that supports all the languages specified
        in the submissions.
    """
    # User explicitly passed a client.
    if isinstance(client, Client):
        logger.debug(f"Using explicitly provided client: {client}")
        return client

    # NOTE: At the moment, we do not support the option to check if explicit
    # flavor of a client supports the submissions, i.e. submissions argument is
    # ignored if flavor argument is provided.

    if isinstance(client, Flavor):
        logger.debug(f"Resolving client from flavor: {client}")
        return get_client(client)

    if client is None:
        if (
            isinstance(submissions, Iterable) and len(submissions) == 0
        ) or submissions is None:
            raise ValueError("Client cannot be determined from empty submissions.")

    # client is None and we have to determine a flavor of the client from the
    # the submission's languages.
    if isinstance(submissions, Submission):
        submissions = [submissions]

    # Check which client supports all languages from the provided submissions.
    languages = [submission.language for submission in submissions]
    logger.debug(f"Attempting to resolve client for languages: {languages}")

    for flavor in Flavor:
        client = get_client(flavor)
        if client is not None and all(
            (client.is_language_supported(lang) for lang in languages)
        ):
            logger.debug(f"Resolved client {client} for languages {languages}")
            return client

    raise ClientResolutionError(
        "Failed to resolve the client from submissions argument. "
        "None of the implicit clients supports all languages from the submissions. "
        "Please explicitly provide the client argument."
    )


def create_submissions(
    *,
    client: Client | Flavor | None = None,
    submissions: Submission | Submissions | None = None,
) -> Submission | Submissions:
    """Universal function for creating submissions to the client.

    Parameters
    ----------
    client : Client or Flavor, optional
        A client or client flavor where submissions should be created.
    submissions: Submission or Submissions, optional
        Submission(s) to create.

    Raises
    ------
    ClientResolutionError
        Raised if client resolution fails.
    """
    client = _resolve_client(client=client, submissions=submissions)

    if isinstance(submissions, Submission):
        logger.info("Creating a single submission.")
        return client.create_submission(submissions)

    logger.info(f"Creating {len(submissions)} submissions.")
    result_submissions = []
    for submission_batch in batched(
        submissions, client.config.max_submission_batch_size
    ):
        if len(submission_batch) > 1:
            result_submissions.extend(client.create_submissions(submission_batch))
        else:
            result_submissions.append(client.create_submission(submission_batch[0]))

    return result_submissions


def get_submissions(
    *,
    client: Client | Flavor | None = None,
    submissions: Submission | Submissions | None = None,
    fields: str | Iterable[str] | None = None,
) -> Submission | Submissions:
    """Get submission (status) from a client.

    Parameters
    ----------
    client : Client or Flavor, optional
        A client or client flavor where submissions should be checked.
    submissions : Submission or Submissions, optional
        Submission(s) to update.
    fields : str or sequence of str, optional
        Submission attributes that need to be updated. Defaults to all attributes.

    Raises
    ------
    ClientResolutionError
        Raised if client resolution fails.
    """
    client = _resolve_client(client=client, submissions=submissions)

    if isinstance(submissions, Submission):
        logger.debug("Getting status for a single submission.")
        return client.get_submission(submissions, fields=fields)

    logger.debug(f"Getting status for {len(submissions)} submissions.")
    result_submissions = []
    for submission_batch in batched(
        submissions, client.config.max_submission_batch_size
    ):
        if len(submission_batch) > 1:
            result_submissions.extend(
                client.get_submissions(submission_batch, fields=fields)
            )
        else:
            result_submissions.append(
                client.get_submission(submission_batch[0], fields=fields)
            )

    return result_submissions


def wait(
    *,
    client: Client | Flavor | None = None,
    submissions: Submission | Submissions | None = None,
    retry_strategy: RetryStrategy | None = None,
) -> Submission | Submissions:
    """Wait for all the submissions to finish.

    Parameters
    ----------
    client : Client or Flavor, optional
        A client or client flavor where submissions should be checked.
    submissions : Submission or Submissions
        Submission(s) to wait for.
    retry_strategy : RetryStrategy, optional
        A retry strategy.

    Returns
    -------
    Submission or Submissions
        A single submission or a list of submissions.

    Raises
    ------
    ClientResolutionError
        Raised if client resolution fails.
    """
    client = _resolve_client(client, submissions)

    if retry_strategy is None:
        if client.retry_strategy is None:
            retry_strategy = RegularPeriodRetry()
        else:
            retry_strategy = client.retry_strategy

    if isinstance(submissions, Submission):
        submissions_list = [submissions]
    else:
        submissions_list = submissions

    submissions_to_check = {
        submission.token: submission for submission in submissions_list
    }

    logger.info(f"Waiting for {len(submissions_to_check)} submissions to finish.")
    while len(submissions_to_check) > 0 and not retry_strategy.is_done():
        logger.debug(f"Checking {len(submissions_to_check)} submissions...")
        get_submissions(client=client, submissions=list(submissions_to_check.values()))
        finished_submissions = [
            token
            for token, submission in submissions_to_check.items()
            if submission.is_done()
        ]
        logger.debug(f"{len(finished_submissions)} submissions finished in this step.")
        for token in finished_submissions:
            submissions_to_check.pop(token)

        # Don't wait if there is no submissions to check for anymore.
        if len(submissions_to_check) == 0:
            break

        retry_strategy.wait()
        retry_strategy.step()

    return submissions


def create_submissions_from_test_cases(
    submissions: Submission | Submissions,
    test_cases: TestCaseType | TestCases | None = None,
) -> Submission | list[Submission]:
    """Create submissions from the submission and test case pairs.

    Function always returns a deep copy so make sure you are using the
    returned submission(s).

    Parameters
    ----------
    submissions : Submission or Submissions
        Base submission(s) that need to be expanded with test cases.
    test_cases: TestCaseType or TestCases
        Test cases.

    Returns
    -------
    Submissions or Submissions
        A single submission if submissions arguments is of type Submission or
        source_code argument is provided, and test_cases argument is of type
        TestCase. Otherwise returns a list of submissions.
    """
    if isinstance(submissions, Submission):
        submissions_list = [submissions]
    else:
        submissions_list = submissions

    if isinstance(test_cases, TestCase) or test_cases is None:
        test_cases_list = [test_cases]
        multiple_test_cases = False
    else:
        try:
            # Let's assume that we are dealing with multiple test_cases that
            # can be created from test_cases argument. If this fails, i.e.
            # raises a ValueError, we know we are dealing with a test_cases=dict,
            # or test_cases=["in", "out"], or test_cases=tuple("in", "out").
            test_cases_list = [TestCase.from_record(tc) for tc in test_cases]

            # It is possible to send test_cases={}, or test_cases=[], or
            # test_cases=tuple([]). In this case, we are treating that as None.
            if len(test_cases) > 0:
                multiple_test_cases = True
            else:
                multiple_test_cases = False
                test_cases_list = [None]
        except ValueError:
            test_cases_list = [test_cases]
            multiple_test_cases = False

    test_cases_list = [TestCase.from_record(test_case=tc) for tc in test_cases_list]

    all_submissions = []
    for submission in submissions_list:
        for test_case in test_cases_list:
            submission_copy = submission.pre_execution_copy()
            if test_case is not None:
                submission_copy.stdin = test_case.input
                submission_copy.expected_output = test_case.expected_output
            all_submissions.append(submission_copy)

    if isinstance(submissions, Submission) and (not multiple_test_cases):
        return all_submissions[0]
    else:
        return all_submissions


def _execute(
    *,
    client: Client | Flavor | None = None,
    submissions: Submission | Submissions | None = None,
    source_code: str | None = None,
    test_cases: TestCaseType | TestCases | None = None,
    wait_for_result: bool = False,
    **kwargs,
) -> Submission | Submissions:
    if submissions is not None and source_code is not None:
        raise ValueError(
            "Both submissions and source_code arguments are provided. "
            "Provide only one of the two."
        )
    if submissions is None and source_code is None:
        raise ValueError("Neither source_code nor submissions argument are provided.")

    # Internally, let's rely on Submission's dataclass.
    if source_code is not None:
        submissions = Submission(source_code=source_code, **kwargs)

    logger.info("Starting execution process.")
    client = _resolve_client(client=client, submissions=submissions)
    all_submissions = create_submissions_from_test_cases(submissions, test_cases)
    all_submissions = create_submissions(client=client, submissions=all_submissions)

    if wait_for_result:
        return wait(client=client, submissions=all_submissions)
    else:
        return all_submissions


def async_execute(
    *,
    client: Client | Flavor | None = None,
    submissions: Submission | Submissions | None = None,
    source_code: str | None = None,
    test_cases: TestCaseType | TestCases | None = None,
    **kwargs,
) -> Submission | Submissions:
    """Create submission(s).

    Aliases: `async_run`.

    Parameters
    ----------
    client : Client or Flavor, optional
        A client where submissions should be created. If None, will try to be
        resolved.
    submissions : Submission or Submissions, optional
        Submission or submissions for execution.
    source_code : str, optional
        A source code of a program.
    test_cases : TestCaseType or TestCases, optional
        A single test or a list of test cases
    **kwargs : dict
        Additional keyword arguments to pass to the Submission constructor.

    Returns
    -------
    Submission or Submissions
        A single submission if submissions arguments is of type Submission or
        source_code argument is provided, and test_cases argument is of type
        TestCase. Otherwise returns a list of submissions.

    Raises
    ------
    ClientResolutionError
        If client cannot be resolved from the submissions or the flavor.
    ValueError
        If both or neither submissions and source_code arguments are provided.
    """
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        test_cases=test_cases,
        wait_for_result=False,
        **kwargs,
    )


def sync_execute(
    *,
    client: Client | Flavor | None = None,
    submissions: Submission | Submissions | None = None,
    source_code: str | None = None,
    test_cases: TestCaseType | TestCases | None = None,
    **kwargs,
) -> Submission | Submissions:
    """Create submission(s) and wait for their finish.

    Aliases: `execute`, `run`, `sync_run`.

    Parameters
    ----------
    client : Client or Flavor, optional
        A client where submissions should be created. If None, will try to be
        resolved.
    submissions : Submission or Submissions, optional
        Submission(s) for execution.
    source_code: str, optional
        A source code of a program.
    test_cases: TestCaseType or TestCases, optional
        A single test or a list of test cases
    **kwargs : dict
        Additional keyword arguments to pass to the Submission constructor.

    Returns
    -------
    Submission or Submissions
        A single submission if submissions arguments is of type Submission or
        source_code argument is provided, and test_cases argument is of type
        TestCase. Otherwise returns a list of submissions.

    Raises
    ------
    ClientResolutionError
        If client cannot be resolved from the submissions or the flavor.
    ValueError
        If both or neither submissions and source_code arguments are provided.
    """
    return _execute(
        client=client,
        submissions=submissions,
        source_code=source_code,
        wait_for_result=True,
        test_cases=test_cases,
        **kwargs,
    )


execute = sync_execute
run = sync_execute
sync_run = sync_execute
async_run = async_execute

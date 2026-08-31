Overview
========

The Judge0 Python SDK has two layers:

* a **high-level API** that creates submissions, expands test cases, batches
  requests, and optionally waits for results;
* a **low-level API** on :class:`~judge0.clients.Client` that maps one-to-one
  to Judge0 HTTP routes.

Most applications should start with :func:`judge0.run`. Use the client methods
when you need a single HTTP call, custom polling, or server metadata.

High-level and low-level API
----------------------------

High-level functions live in :mod:`judge0.api`. The entry-point functions
(:func:`judge0.run`, :func:`judge0.async_run`, :func:`judge0.wait`, and
:func:`judge0.get_client`) are re-exported from the ``judge0`` package.
They accept either source code, a
:class:`~judge0.submission.Submission`, or a sequence of submissions. If you
omit ``client``, the SDK resolves one from the environment. See
:doc:`client_resolution`.

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Function
     - Role
   * - :func:`judge0.run` / :func:`judge0.execute` / :func:`judge0.sync_run`
     - Create submission(s) and wait until they finish. These names are aliases
       of :func:`judge0.api.sync_execute`.
   * - :func:`judge0.async_run` / :func:`judge0.async_execute`
     - Create submission(s) and return immediately. These are **not**
       ``asyncio`` coroutines.
   * - :func:`judge0.wait`
     - Poll existing submission(s) until they finish or the retry strategy
       stops.
   * - :func:`judge0.get_client`
     - Resolve the implicit client for CE (``Flavor.CE``) or Extra CE
       (``Flavor.EXTRA_CE``).
   * - :func:`judge0.api.create_submissions`
     - Send already-built submissions, splitting them into batches that fit
       the server limit.
   * - :func:`judge0.api.get_submissions`
     - Refresh status and result fields on existing submissions.
   * - :func:`judge0.api.create_submissions_from_test_cases`
     - Expand one or more submissions across test cases. Used internally by
       :func:`judge0.run`.

The low-level API is the methods on :class:`~judge0.clients.Client`:

* :meth:`~judge0.clients.Client.create_submission` /
  :meth:`~judge0.clients.Client.create_submissions`
* :meth:`~judge0.clients.Client.get_submission` /
  :meth:`~judge0.clients.Client.get_submissions`
* :meth:`~judge0.clients.Client.get_languages`,
  :meth:`~judge0.clients.Client.get_language`,
  :meth:`~judge0.clients.Client.get_statuses`,
  :meth:`~judge0.clients.Client.get_about`,
  :meth:`~judge0.clients.Client.get_config_info`

Low-level calls do not wait for execution, do not expand test cases, and do
not pick a client for you. ``create_submissions`` and ``get_submissions`` on
the client cannot send more items than
``client.config.max_submission_batch_size``. The high-level helpers batch
automatically.

``async_run`` versus ``run``
----------------------------

:func:`judge0.run` blocks until Judge0 reports a terminal status or the
client's retry strategy is exhausted, which may return a queued or processing
submission.
:func:`judge0.async_run` only creates the submission(s) and returns the
submission objects with their token fields populated.
Call :func:`judge0.wait` later, or poll with
:func:`judge0.api.get_submissions`.

.. code-block:: python

    import judge0

    submission = judge0.async_run(source_code="print('hello, world')")
    print(submission.stdout)  # None; the job is not finished yet.

    judge0.wait(submissions=submission)
    print(submission.stdout)  # hello, world

Important classes
-----------------

* :class:`~judge0.clients.Client`: HTTP client for one Judge0 server.
  Provider subclasses include :class:`~judge0.clients.Judge0CloudCE`,
  :class:`~judge0.clients.RapidJudge0CE`, and
  :class:`~judge0.clients.ATDJudge0CE`, plus the Extra CE variants.
* :class:`~judge0.submission.Submission`: request and response for one
  program run. Set ``source_code``, ``language``, ``stdin``, and optional
  limits before sending. After execution, read ``stdout``, ``stderr``,
  ``status``, ``time``, and ``memory``.
* :class:`~judge0.base_types.TestCase`: pair of ``input`` and
  ``expected_output``. :func:`judge0.run` also accepts tuples, lists, and
  dicts and normalizes them to this type.
* :class:`~judge0.base_types.LanguageAlias` and
  :class:`~judge0.base_types.Flavor`: language aliases such as
  ``judge0.PYTHON`` or ``judge0.C``, and the CE / Extra CE flavors used
  for client resolution.
* :class:`~judge0.base_types.Status`: submission status, including
  ``Accepted``, compile errors, and runtime errors.
* :class:`~judge0.filesystem.File` and
  :class:`~judge0.filesystem.Filesystem`: extra files sent with a
  submission, or files produced after execution.
* :class:`~judge0.retry.RegularPeriodRetry`,
  :class:`~judge0.retry.MaxRetries`, and
  :class:`~judge0.retry.MaxWaitTime`: polling strategies used by
  :func:`judge0.wait`.

Typical flow
------------

1. Build source code or a :class:`~judge0.submission.Submission`.
2. Optionally attach test cases or extra files.
3. Call :func:`judge0.run`, or :func:`judge0.async_run` plus
   :func:`judge0.wait`.
4. Inspect ``stdout``, ``status``, and other result fields.

.. code-block:: python

    import judge0

    result = judge0.run(
        source_code="print(f'Hello, {input()}!')",
        language=judge0.PYTHON,
        test_cases=[
            ("Ada", "Hello, Ada!"),
            {"input": "Bob", "expected_output": "Hello, Bob!"},
        ],
    )

    for case in result:
        print(case.status, case.stdout)

Pass an explicit client when you do not want implicit resolution:

.. code-block:: python

    import judge0

    client = judge0.RapidJudge0CE(api_key="xxx")
    result = judge0.run(client=client, source_code="print(42)")
    print(result.stdout)

For the full parameter lists, see the :doc:`/api/api` reference, the
:doc:`/api/clients` reference, and the :doc:`/api/submission` reference.

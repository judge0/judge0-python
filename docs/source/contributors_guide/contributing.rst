Contributing
============

Preparing the development setup
-------------------------------

1. Install `uv <https://docs.astral.sh/uv/getting-started/installation/>`_.
2. Fork the repository (in GitHub) and clone the forked repository:

.. code-block:: console

    $ git clone https://github.com/<username>/judge0-python
    $ cd judge0-python

3. Prepare the virtual environment and dependencies:

.. code-block:: console

    $ uv sync --group dev

4. Install the necessary development tools:

.. code-block:: console

    $ uv tool install pre-commit

5. Make sure all the necessary tools are installed:

.. code-block:: console

    $ uv tool list

6. Finally, install the pre-commit hooks:

.. code-block:: console

    $ uv tool run pre-commit install

Building documentation
----------------------

Documentation is built using Sphinx. While working on a documentation, you can run

.. code-block:: console

    $ cd docs
    $ make livehtml

The ``make livehtml`` command will start a live HTTP server, watch the `docs` directory for changes,
and rebuild the documentation on every change, enabling you to continuously work on the documentation,
without having to manually rebuild it after every change.

You can inspect the changes by opening the ``http://localhost:8000`` in your browser.

.. You'll see a different output since the documentation is build with
.. `sphinx-multiversion <https://github.com/sphinx-contrib/multiversion>`_ extension.

Testing
-------

.. warning::
    If you are implementing features or fixing bugs, you are expected to have
    all API keys (RapidAPI and ATD) setup and set in you
    environment variables - ``JUDGE0_RAPID_API_KEY``,
    and ``JUDGE0_ATD_API_KEY``.

Every bug fix or new feature should have tests for it. The tests are located in
the ``tests`` directory and are written using `pytest <https://docs.pytest.org/en/stable/>`_.

While working with the tests, you should use the following fixtures:

* ``ce_client`` - a client, chosen based on the environment variables set, that uses the CE flavor of the client.
* ``extra_ce_client`` - a client, chosen based on the environment variables set, that uses the Extra CE flavor of the client.

The ``ce_client`` and ``extra_ce_client`` are fixtures that
return a client based on the environment variables set. This enables you to
run the full test suite locally, but also to run the tests on the CI pipeline
without changing the tests.

You can use the fixtures in your tests like this:

.. code-block:: python

    def test_my_test(request):
        client = request.getfixturevalue("ce_client") # or extra_ce_client

To run the tests locally, you can use the following command:

.. code-block:: console

    $ pytest tests -k '<test_name>'

This will enable you to run a single test, without incurring the cost of
running the full test suite. If you want to run the full test suite, you can
use the following command:

.. code-block:: console

    $ pytest tests

or you can create a draft PR and let the CI pipeline run the tests for you.
The CI pipeline will run the tests on every PR, using a private instance
of Judge0, so you can be sure that your changes are not breaking the existing
functionality.

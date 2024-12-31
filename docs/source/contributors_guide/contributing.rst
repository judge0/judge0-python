Contributing
============

Preparing the development setup
-------------------------------

1. Install Python 3.9

.. code-block:: console

    $ sudo add-apt-repository ppa:deadsnakes/ppa
    $ sudo apt update
    $ sudo apt install python3.9 python3.9-venv

2. Clone the repo, create and activate a new virtual environment

.. code-block:: console

    $ cd judge0-python
    $ python3.9 -m venv venv
    $ . venv/bin/activate

3. Install the library and development dependencies

.. code-block:: console

    $ pip install -e .[test]
    $ pip install -r docs/requirements.txt # needed for building the docs
    $ pre-commit install

Building documentation
----------------------

Documentation is built using Sphinx. To build the documentation, run the

.. code-block:: console

    $ cd docs
    $ make html

You should inspect the changes in the documentation by opening the
``docs/build/html/index.html`` file in your browser.

You'll see a different output since the documentation is build with
`sphinx-multiversion <https://github.com/sphinx-contrib/multiversion>`_ extension.

Testing
-------

If you implemented a feature or fixed a bug, please add tests for it.

Unfortunately, at the moment you cannot run full test suite because it requires
access to API keys for all implemented API hubs (ATD, Sulu, and RapidAPI) and
a private Judge0 instance. To partially address this situation, you can run and
test your implemented feature and tests locally and use the GitHub CI pipeline
to run the full test suite.

To run the tests locally, you can use the following command:

.. code-block:: console

    $ pytest -svv tests -k '<test_name>'

To make the test compatible with the CI pipeline, you should use one of the
client fixtures:

.. code-block:: python
    
    def test_my_test(request):
        client = request.getfixturevalue("judge0_ce_client") # or judge0_extra_ce_client

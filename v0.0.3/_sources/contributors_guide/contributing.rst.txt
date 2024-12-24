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
    $ pre-commit install

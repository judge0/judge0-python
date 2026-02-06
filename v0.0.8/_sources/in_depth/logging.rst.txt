Logging
=======

By default, judge0 Python SDK does not emit logs. To turn on logging, using
default settings, add the `JUDGE0_ENABLE_LOGGING=1` to your environment variables.

For instance, to run one of the examples with logging enabled:

.. code-block:: console

    $ JUDGE0_ENABLE_LOGGING=1 python examples/0001_hello_world.py 

You should see basic info logs and where the file logs are stored.

To modify default log levels for console and file logs, `INFO` and `WARNING` respectively,
you can set the corresponding environment variables: `JUDGE0_CONSOLE_LOG_LEVEL` and `JUDGE0_FILE_LOG_LEVEL`
to one of the appropriate log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.

For instance, setting the console level to debug should show additional debug logs: 

.. code-block:: console

    $ JUDGE0_ENABLE_LOGGING=1 JUDGE0_CONSOLE_LOG_LEVEL=debug python examples/0001_hello_world.py 
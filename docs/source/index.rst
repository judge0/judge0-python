===============================
Judge0 Python SDK documentation
===============================

Getting Started
===============

You can run minimal Hello World example in three easy steps:

1. Install Judge0 Python SDK:

.. code-block:: bash

    pip install judge0

2. Create a minimal script:

.. code-block:: python

    import judge0

    submission = judge.run(source_code="print('Hello Judge0!')")
    print(submission.stdout)

3. Run the script.

Want to learn more
==================

To learn what is happening behind the scenes and how to best use Judge0 Python
SDK to facilitate the development of your own product see In Depth guide and
Examples.

Getting Involved
================

TODO

.. toctree::
      :caption: API
      :glob:
      :titlesonly:
      :hidden:

      api/api
      api/submission
      api/clients
      api/types

.. toctree::
      :caption: Getting Involved
      :glob:
      :titlesonly:
      :hidden:

      contributors_guide/contributing
      contributors_guide/release_notes
=================
Judge0 Python SDK
=================

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
`examples <https://github.com/judge0/judge0-python/tree/master/examples>`_.

Getting Involved
================

Getting involved in any open-source project is simple and rewarding, with
multiple ways to contribute to its growth and success. You can help by:

1. `reporting bugs <https://github.com/judge0/judge0-python/issues>`_ by
   creating a detailed issue describing the problem, along with any relevant code or
   steps to reproduce it, so it can be addressed effectively,
2. creating a `pull request <https://github.com/judge0/judge0-python/pulls>`_ for
   an existing issue; we welcome improvements, fixes, and new features that align
   with the project's goals, and
3. you can show support by starring the `repository <https://github.com/judge0/judge0-python>`_,
   letting us know that we’re doing a good job and helping us gain visibility within
   the open-source community.

Every contribution, big or small, is valuable!

.. toctree::
      :caption: API
      :glob:
      :titlesonly:
      :hidden:

      api/api
      api/clients
      api/errors
      api/filesystem
      api/retry
      api/submission
      api/types


.. toctree::
      :caption: In Depth
      :glob:
      :titlesonly:
      :hidden:

      in_depth/client_resolution


.. toctree::
      :caption: Getting Involved
      :glob:
      :titlesonly:
      :hidden:

      contributors_guide/contributing
      contributors_guide/release_notes

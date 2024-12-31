How to create a release
=======================

Creating a release is a simple process that involves a few steps:

#. **Prepare the release**:
    #. Create a separate branch for the release. Name the branch ``release-x.y.z``
       where ``x.y.z`` is the version number.
    #. Update the version number in ``judge0/__init__.py``.
    #. Update the version number in ``judge0/pyproject.toml``.
    #. Sync the branch with any changes from the master branch.
    #. Create a pull request for the release branch. Make sure that all tests pass.
    #. Merge the pull request.
    #. Pull the changes to your local repository and tag the commit (``git tag vX.Y.Z``) with the version number.
    #. Push the tags to the remote repository (``git push origin master --tags``).
#. **Create release (notes) on GitHub**.
    #. Go to the `releases page <https://github.com/judge0/judge0-python/releases/new>`_ on GitHub.
    #. Release title should be ``Judge0 Python SDK vX.Y.Z``.
    #. Release notes should include a changes from the previous release to the newest release.
    #. Use the `template <https://github.com/judge0/judge0-python/blob/master/RELEASE_NOTES_TEMPLATE.md>`_ from the repo to organize the changes.
    #. Create the release. ("Set as a pre-release" should NOT be checked.)
#. **Release on PyPI**:
    #. Use the `GitHub Actions workflow <https://github.com/judge0/judge0-python/actions/workflows/publish.yml>`_ to create a release on PyPI.
    #. Select `Run workflow` and as `Target repository` select `pypi`.
    #. Click the `Run workflow` button.

After the release is successfully published on PyPI, create a new pull request
that updates the working version in  ``judge0/__init__.py`` and ``judge0/pyproject.toml``
to the minor version. Merge the pull request and you're done! For example, if the
new release was ``1.2.2``, the working version should be updated to ``1.3.0.dev0``.

You've successfully created a release! Congratulations! 🎉
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import os
import sys

project = "Judge0 Python SDK"
copyright = "2024, Judge0"
author = "Judge0"
release = ""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    # "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
    "sphinx_multiversion",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_show_sphinx = False
html_sidebars = {
    "**": [
        "sidebar_main_nav_links.html",
        "sidebar_toc.html",
        "versioning.html",
    ],
}

sys.path.insert(0, os.path.abspath("../../src/"))  # Adjust as needed


autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "special-members": False,
    "inherited-members": False,
}
autodoc_mock_imports = ["requests", "pydantic"]

napoleon_google_docstring = False

# Whitelist pattern for tags (set to None to ignore all tags)
smv_tag_whitelist = r"^.*$"
# Whitelist pattern for branches (set to None to ignore all branches)
smv_branch_whitelist = r"^master$"
# Whitelist pattern for remotes (set to None to use local branches only)
smv_remote_whitelist = None
# Pattern for released versions
smv_released_pattern = ""  # r"^tags/.*$"
# Format for versioned output directories inside the build directory
smv_outputdir_format = "{ref.name}"
# Determines whether remote or local git branches/tags are preferred if their
# output dirs conflict
smv_prefer_remote_refs = False

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import os
import sys

from sphinxawesome_theme.postprocess import Icons

project = "Judge0 Python SDK"
copyright = "2025, Judge0"
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

html_title = project
html_theme = "sphinxawesome_theme"
html_theme_options = {
    "show_scrolltop": True,
    "extra_header_link_icons": {
        "repository on GitHub": {
            "link": "https://github.com/judge0/judge0-python",
            "icon": (
                '<svg height="26px" style="margin-top:-2px;display:inline" '
                'viewBox="0 0 45 44" '
                'fill="currentColor" xmlns="http://www.w3.org/2000/svg">'
                '<path fill-rule="evenodd" clip-rule="evenodd" '
                'd="M22.477.927C10.485.927.76 10.65.76 22.647c0 9.596 6.223 17.736 '
                "14.853 20.608 1.087.2 1.483-.47 1.483-1.047 "
                "0-.516-.019-1.881-.03-3.693-6.04 "
                "1.312-7.315-2.912-7.315-2.912-.988-2.51-2.412-3.178-2.412-3.178-1.972-1.346.149-1.32.149-1.32 "  # noqa
                "2.18.154 3.327 2.24 3.327 2.24 1.937 3.318 5.084 2.36 6.321 "
                "1.803.197-1.403.759-2.36 "
                "1.379-2.903-4.823-.548-9.894-2.412-9.894-10.734 "
                "0-2.37.847-4.31 2.236-5.828-.224-.55-.969-2.759.214-5.748 0 0 "
                "1.822-.584 5.972 2.226 "
                "1.732-.482 3.59-.722 5.437-.732 1.845.01 3.703.25 5.437.732 "
                "4.147-2.81 5.967-2.226 "
                "5.967-2.226 1.185 2.99.44 5.198.217 5.748 1.392 1.517 2.232 3.457 "
                "2.232 5.828 0 "
                "8.344-5.078 10.18-9.916 10.717.779.67 1.474 1.996 1.474 4.021 0 "
                "2.904-.027 5.247-.027 "
                "5.96 0 .58.392 1.256 1.493 1.044C37.981 40.375 44.2 32.24 44.2 "
                '22.647c0-11.996-9.726-21.72-21.722-21.72" '
                'fill="currentColor"/></svg>'
            ),
        },
    },
    "awesome_external_links": True,
    "main_nav_links": {
        "Home": "https://judge0.github.io/judge0-python/",
        "Judge0": "https://judge0.com/",
    },
}
html_show_sphinx = False
html_sidebars = {
    "**": [
        "sidebar_main_nav_links.html",
        "sidebar_toc.html",
        "versioning.html",
    ],
}
html_logo = "../assets/logo.png"
html_favicon = html_logo
pygments_style = "sphinx"

sys.path.insert(0, os.path.abspath("../../src/"))  # Adjust as needed

# -- Awesome theme config --
html_permalinks_icon = Icons.permalinks_icon

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
smv_tag_whitelist = r"^v[0-9]+\.[0-9]+\.[0-9]+$"
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

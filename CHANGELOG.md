# Changelog

## v0.1.0-dev

- Show only the last 10 documentation versions in the sidebar, collapse older
  tags under "View more...", and document how to open older docs in the FAQ.
- Fix Sphinx autodoc imports for Pydantic-backed submission types.
- Add complete static typing across the SDK and tests, with typed single and batch
  submission return values.
- Parse Judge0 UTC timestamps as timezone-aware values and validate submission
- Replace Flake8 and ufmt checks with pinned Ruff and Pyright hooks.
  source code and batch tokens before serialization.
- Pin Ruff, Pyright, and pre-commit as project-scoped dependencies in the dev
  `lint` group, replacing global `uv tool` installs for reproducible setups.
- Add `AGENTS.md` and `CHANGELOG.md`

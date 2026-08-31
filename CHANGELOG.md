# Changelog

## v0.1.0-dev

- Rename "preview" terminology to "free tier cloud" and rename the
  `JUDGE0_SUPPRESS_PREVIEW_WARNING` environment variable to
  `JUDGE0_SUPPRESS_FREE_TIER_CLOUD_WARNING`.
- Bump the uv version used in GitHub Actions from 0.9.8 to 0.11.33 so that the
  CI can parse the relative `exclude-newer` value in `pyproject.toml`.
- Document the general API overview: high-level versus low-level functions,
  core types, and the typical `run` / `async_run` flow.
- Fix Sphinx autodoc imports for Pydantic-backed submission types.
- Add complete static typing across the SDK and tests, with typed single and batch
  submission return values.
- Parse Judge0 UTC timestamps as timezone-aware values and validate submission
- Replace Flake8 and ufmt checks with pinned Ruff and Pyright hooks.
  source code and batch tokens before serialization.
- Pin Ruff, Pyright, and pre-commit as project-scoped dependencies in the dev
  `lint` group, replacing global `uv tool` installs for reproducible setups.
- Add `AGENTS.md` and `CHANGELOG.md`

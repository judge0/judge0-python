# AGENTS.md

## Project management

- Project and all its dependencies are managed via `uv`
- Use `uv` to add dependencies, remove dependencies, run tests, run standalone scripts, etc.
- Use `uv run python` to run Python within the local environment with all dependencies
- Use `uv run pytest` to run tests
- Use `uv run python scripts/<script>.py` to run scripts
- Do not edit `pyproject.toml` directly, use `uv`! If you need to, ask for permission!

## Project structure

- `src/judge0/` contains the installable Judge0 SDK package. Keep runtime code, public APIs, models, clients, retry behavior, and package utilities here. Its modules are:
  - `__init__.py` defines the public package API, resolves implicit clients from environment configuration, enables optional logging, and exposes flavor and language aliases.
  - `_logging.py` configures package-level console and rotating-file logging, including environment-controlled log levels.
  - `api.py` provides high-level client resolution and submission orchestration: creating, retrieving, polling, and executing submissions. Its `async_*` helpers return after submission creation without waiting for results; they are not `asyncio` coroutines.
  - `base_types.py` defines shared models, protocols, type aliases, and enums for test cases, languages, client flavors, submission statuses, and server configuration.
  - `clients.py` implements the base HTTP client and the provider- and flavor-specific clients for Judge0 Cloud, RapidAPI, and AllThingsDev.
  - `common.py` contains shared base64 encoding and decoding helpers and iterable batching.
  - `data.py` maps language aliases to Judge0 language IDs by server version and flavor.
  - `errors.py` defines SDK-specific exception types for client resolution and preview-client usage limits.
  - `filesystem.py` models individual files and ZIP-backed collections used for additional and post-execution files.
  - `retry.py` defines the polling strategy interface and retry-count, wait-time, and periodic retry implementations.
  - `submission.py` models submission request and response data, including serialization, response updates, completion checks, and execution filesystem handling.
  - `utils.py` detects HTTP rate-limit responses and translates preview-client rate limits into SDK-specific errors.
  - `version.py` exposes the package version constant.
- `tests/` contains the pytest suite. Shared fixtures belong in `conftest.py`, and focused tests should use `test_<area>.py` modules that correspond to SDK behavior.
- `examples/` contains runnable SDK usage examples, including the standalone HTTP callback example in `examples/1000_http_callback_aka_webhook/`.
- `docs/source/` contains the Sphinx documentation sources. API reference pages live in `docs/source/api/`, contributor documentation in `docs/source/contributors_guide/`, conceptual guides in `docs/source/in_depth/`, and the FAQ in `docs/source/faq.rst`. Sphinx configuration and templates also live under `docs/source/`; `docs/assets/` contains documentation assets.
- `.github/` contains CI workflows and GitHub issue templates.
- `pyproject.toml` defines package metadata, dependencies, dependency groups, and tool configuration; `uv.lock` pins the resolved environment. Manage both through `uv` as described above.
- Root-level Markdown files contain the project overview, contribution and conduct policies, release-note template, changelog, and agent instructions.
- Generated directories and files such as `.venv/`, `dist/`, `htmlcov/`, `docs/build/`, coverage data, and tool caches are not source and should not be edited manually.

## Development workflow

- Start every implementation task from `master` unless the user explicitly instructs otherwise:
  - Run `git status --short --branch` before making changes.
  - Switch to `master`.
  - Create a new task branch from `master`.
  - If local changes block switching or branching, stop and ask how to proceed; do not stash, revert, or overwrite user changes without explicit approval.
- Branch names and commit titles must follow the task category:
  - New feature: `feature/<short-slug>` branch and `feat: <title>` commit.
  - Bug fix: `bugfix/<short-slug>` branch and `fix: <title>` commit.
  - Code cleanup without behavior changes: `refactor/<short-slug>` branch and `refactor: <title>` commit.
  - Maintenance: `chore/<short-slug>` branch and `chore: <title>` commit.
  - Documentation: `docs/<short-slug>` branch and `docs: <title>` commit.
- Follow Test Driven Development for code changes:
  1. Write or update focused tests before changing implementation code.
  2. Run the relevant `uv run pytest ...` command and confirm the tests fail for the expected reason.
  3. Write the minimal working implementation.
  4. Re-run the focused tests, then run the broader relevant test suite.
  5. Refactor only after tests pass, and re-run tests after refactoring.
- Split final work into multiple reviewable commits when the task has multiple subtasks. Each commit should contain the tests and implementation for one coherent subtask, and each commit title must use the category prefix above.
- After changes are done or applied, prepare a proposed commit message that follows the required category prefix format.

## Code Conventions

- Use Python 3.10+ type annotations (e.g. instead of `Union[str, int]` write `str | int`)
- Ignore `# TODO`s in the code comments
- Always update `CHANGELOG.md` with a clear and concise description of changes
- Follow numpydoc style for documentation
- Every function and method parameter should be type annotated
- Every function and method should have a return type annotated
- Function and method docstring should include raised exceptions/errors
- Document recommended default values in `.env.example`.
- Do not import `from __future__ import annotations`

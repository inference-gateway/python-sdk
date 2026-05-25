# Repository Guidelines

## Project Structure & Module Organization

This repository is the Python SDK for Inference Gateway. The importable package lives in `inference_gateway/`: `client.py` contains the hand-written synchronous client, `models.py` contains generated Pydantic models, and `__init__.py` controls public exports. Tests live in `tests/`, currently centered on client behavior. Runnable usage examples are under `examples/` (`chat`, `list`, `mcp`, `tools`). OpenAPI generation inputs are `openapi.yaml` and `templates/`.

## Build, Test, and Development Commands

Use `task` commands from `Taskfile.yml`:

- `task install` installs the package in editable mode with dev dependencies.
- `task format` runs Black and isort on `inference_gateway/`, `tests/`, and `examples/`.
- `task lint` checks Black, isort, and mypy.
- `task test` runs the pytest suite.
- `task test:coverage` adds terminal and HTML coverage reports.
- `task generate` downloads and validates the OpenAPI spec, then regenerates `inference_gateway/models.py`.
- `task build` cleans, lints, tests, and builds the package.

For a focused test, use `pytest tests/test_client.py::test_list_models -v`.

## Coding Style & Naming Conventions

Python requires 4-space indentation and LF line endings. YAML and JSON use 2-space indentation. Black and isort are configured for 100-character lines. Prefer typed public functions; mypy is configured with `disallow_untyped_defs = true`. Use `snake_case` for functions, methods, variables, and test names; use `PascalCase` for classes and Pydantic models.

## Testing Guidelines

Tests use pytest and `unittest.mock`. Keep network calls mocked; existing client tests patch `requests.Session.request` and assert exact URL, params, JSON body, and timeout. Name files `test_*.py`, classes `Test*`, and functions `test_*`. Add or update tests when changing client request behavior, error handling, streaming, or public models.

## Generated Code & API Schema

Do not edit `inference_gateway/models.py` directly. Update the upstream schema or local `openapi.yaml`/templates as appropriate, then run `task generate`. If new generated models should be public, update `inference_gateway/__init__.py`. Keep the requests and httpx client paths behaviorally aligned.

## Commit & Pull Request Guidelines

Recent history follows Conventional Commits, such as `chore(deps): ...`, `ci(release): ...`, and `fix: ...`. Use `feat:` for new behavior and `fix:` for bug fixes; use `docs:`, `test:`, `chore:`, `ci:`, `build:`, or `refactor:` where appropriate. Pull requests should describe the change, note tests run, link related issues, and call out generated-code updates or API compatibility concerns.

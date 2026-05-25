# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python SDK for the Inference Gateway — a unified client over multiple LLM providers (OpenAI, Anthropic, Google, Groq, Ollama, etc.). Distributed on PyPI as `inference-gateway`. Requires Python 3.12+ (target 3.13).

The SDK is intentionally thin: a hand-written client (`inference_gateway/client.py`) wrapping auto-generated Pydantic models (`inference_gateway/models.py`).

## Common commands

Tasks are orchestrated with [`task`](https://taskfile.dev) (`Taskfile.yml`):

- `task install` — install dev dependencies (`pip install -e ".[dev]"`)
- `task test` — run pytest suite
- `task test:coverage` — pytest with coverage report (term + html)
- `task lint` — black --check, isort --check-only, and mypy on `inference_gateway/` and `examples/`
- `task format` — apply black + isort
- `task generate` — regenerate `inference_gateway/models.py` from `openapi.yaml` (depends on `oas-download` → fetches the latest spec from `inference-gateway/schemas`)
- `task build` — runs `clean` + `lint` + `test`, then `python -m build`
- `task dev:setup` — full environment bootstrap (install, download OAS, generate, install pre-commit, test)

Run a single test: `pytest tests/test_client.py::test_list_models -v`

Note: CI (`.github/workflows/ci.yml`) only runs `black --check .` and `pytest tests/` — it does NOT run mypy or isort. `task lint` is stricter than CI; pre-commit (`.pre-commit-config.yaml`) catches the rest locally.

## Architecture

### Code generation pipeline

`inference_gateway/models.py` is **auto-generated** by `datamodel-codegen` from `openapi.yaml` (synced from the [`inference-gateway/schemas`](https://github.com/inference-gateway/schemas) repo). Never edit it by hand — changes will be overwritten on the next `task generate`.

The generation uses custom Jinja templates in `templates/` (notably `templates/header.jinja2` for the file header and `templates/pydantic/BaseModel.jinja2` for model rendering). When a new model is needed, the workflow is:

1. Update the spec upstream in `inference-gateway/schemas`
2. Run `task generate` here (downloads latest spec, validates, regenerates)
3. If the new model needs to be public, add it to `inference_gateway/__init__.py`'s imports and `__all__`
4. Update `client.py` if a new endpoint is needed

### Client layer

`InferenceGatewayClient` (`inference_gateway/client.py`) supports two HTTP backends selected via `use_httpx`:

- `requests.Session` (default) — synchronous
- `httpx.Client` — also synchronous but configurable

Both code paths must be kept in sync; `_make_request` and `_process_stream_response` handle the dispatch. Streaming has separate code paths per backend because httpx requires a `with self.client.stream(...)` context manager while requests uses `stream=True` kwarg.

Three exception types form the public error hierarchy: `InferenceGatewayError` (base) → `InferenceGatewayAPIError` (carries `status_code` + `response_data`) and `InferenceGatewayValidationError` (Pydantic validation failures).

### Streaming protocol

`create_chat_completion_stream` yields `SSEvent` objects (not parsed completion chunks). Callers are expected to `json.loads(chunk.data)` and validate against `CreateChatCompletionStreamResponse` themselves — see the README's streaming example. `data: [DONE]` sentinels are filtered out by `_process_stream_response`.

### Provider-specific metadata

Some providers (notably Google Gemini reasoning models) attach opaque per-call metadata like `thought_signature` that must round-trip verbatim on follow-up requests. This is preserved automatically when the caller appends the returned `message` object directly to the conversation. If reconstructing from dicts, the `ToolCallExtraContent` / `Google` models must be populated explicitly. See README "Provider-Specific Tool-Call Metadata".

## Testing

Tests in `tests/test_client.py` use `unittest.mock.patch` on `requests.Session.request` — no live HTTP, no fixtures spinning up servers. When adding client methods, mirror this style: mock the response, assert the exact URL/params/json passed to `request`.

## Release process

Releases are driven by [semantic-release](https://semantic-release.gitbook.io) (`.releaserc.yaml`) and triggered manually via the `Release` GitHub Action workflow. Commit messages **must follow Conventional Commits** because they drive version bumps and changelog sections:

- `feat:` → minor bump
- `fix:`, `perf:`, `refactor:`, `impr:`, `ci:`, `docs:`, `chore:`, `style:`, `test:`, `build:` → patch bump

The release flow bumps `pyproject.toml` version, updates `CHANGELOG.md`, tags as `v${version}`, creates a GitHub release, and publishes to PyPI via twine.

# Repository Guidelines

Python SDK for Inference Gateway — a thin, hand-written synchronous client over auto-generated Pydantic models for the gateway's OpenAI- and Anthropic-compatible APIs. Distributed on PyPI as `inference-gateway`. Requires Python 3.12+.

## Commands

All development runs through `task` (see `Taskfile.yml`):

- `task install` — `pip install -e ".[dev]"`
- `task format` — Black + isort on `inference_gateway/`, `tests/`, `examples/`
- `task lint` — Black `--check`, isort `--check-only`, mypy. Stricter than CI, which only runs Black and pytest.
- `task test` — pytest suite; `task test:coverage` adds terminal + HTML coverage
- `task generate` — fetches/validates the OpenAPI spec, regenerates `inference_gateway/models.py`
- `task build` — clean + lint + test, then `python -m build`
- `task precommit:install` — point git at `.githooks/` (a plain shell script, not the pre-commit framework)

Focused test: `pytest tests/test_client.py::test_list_models -v`

## Layout

- `inference_gateway/client.py` — hand-written `InferenceGatewayClient` with two synchronous backends: `requests.Session` (default) and `httpx.Client` (`use_httpx=True`). Keep both paths behaviorally aligned in `_make_request` and `_process_stream_response`.
- `inference_gateway/models.py` — **auto-generated, do not edit by hand**. Update the spec upstream in `inference-gateway/schemas` (or local `openapi.yaml`/`templates/`), then `task generate`; pin the spec with `SCHEMAS_REF=refs/tags/vX.Y.Z`. New public models also need `inference_gateway/__init__.py` imports and `__all__` entries.
- `tests/` — client behavior; `examples/` — runnable usage examples (chat, list, mcp, messages, tools).

## Style

Black + isort at 100 columns; 4-space indents, LF line endings; YAML/JSON at 2 spaces. mypy with `disallow_untyped_defs = true` and the pydantic plugin. `snake_case` for functions/tests, `PascalCase` for classes and models.

## Testing

pytest + `unittest.mock` only — never make live network calls. Existing tests patch `requests.Session.request` and assert exact URL, params, JSON body, and timeout; mirror that for new client methods. Streaming yields raw `SSEvent` objects — callers parse `chunk.data` themselves. Never commit real API tokens; examples take configuration from env vars.

## Commits & Releases

Conventional Commits drive semantic-release versioning (`.releaserc.yaml`): `feat:` → minor; `fix:`/`perf:`/`refactor:`/`docs:`/`ci:`/`chore:`/`test:`/`build:` → patch. PRs should note tests run and flag generated-code updates or API compatibility concerns.

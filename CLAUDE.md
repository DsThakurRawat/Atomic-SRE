# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Install / sync (uses `uv`, Python 3.12+ required, formatter/linter target is 3.13):

```bash
uv sync --dev
```

Run the interactive CLI (launches the questionary-based setup wizard on first run, then a Local / Remote-Deployment menu):

```bash
uv run atomic-sre
```

Headless single-shot diagnosis (bypasses the CLI; useful for debugging and CI). Positional args fall back to env vars `LOG_GROUP`, `SERVICE_NAME`, `TIME_RANGE_MINUTES`:

```bash
uv run python -m atomic_sre.run <log_group> <service_name> [time_range_minutes]
```

Bring up the agent container plus the Slack MCP sidecar (`korotovsky/slack-mcp-server`) on `:13080`:

```bash
docker compose up -d
```

Tests, single test, and coverage (config in `pyproject.toml`; `--cov=src` is on by default):

```bash
uv run pytest tests
uv run pytest tests/test_get_model.py::test_anthropic_provider_resolves
```

Lint / typecheck / typos / secrets (one command runs the full pre-commit stack — ruff, mypy strict, typos, bandit, trufflehog via Docker):

```bash
uv run pre-commit run --all-files
```

Benchmark suites against Opik (golden datasets live under `src/atomic_sre/benchmarks/{routing,diagnostics}/dataset`):

```bash
uv run atomic-sre-run-tool-call-eval
uv run atomic-sre-run-diagnosis-quality-eval
```

## Architecture

**Reasoning loop is a LangGraph state machine, not a prebuilt ReAct agent.** `engine/orchestrator.py` compiles a `StateGraph` with two nodes — `agent` (calls the LLM with `bind_tools(...)`) and `tools` (a `ToolNode`) — and routes between them via `route_after_model`. The loop terminates when the model emits an `ErrorDiagnosis` tool call that passes Pydantic validation in `_handle_diagnosis_validation`; the validated diagnosis is stashed in `AgentState["diagnosis"]` and `route_after_model` returns `END`. If validation fails, a `ToolMessage` with the structured error is fed back so the model can retry. Multiple concurrent `ErrorDiagnosis` calls are rejected.

**Tools come from three places, with filtering.** `_load_mcp_tools` connects via `MultiServerMCPClient` to (a) the GitHub Copilot MCP (`streamable_http`, bearer token from `GITHUB_PERSONAL_ACCESS_TOKEN`) and (b) the Slack MCP (`sse`, defaults to `http://localhost:13080/sse`). `_filter_mcp_tools` keeps only an allowlist: GitHub `search_code` / `get_file_contents`, Slack `conversations_add_message`. If the Slack MCP is unreachable, a fallback `@tool` is registered that logs to console so the graph still runs end to end. CloudWatch tools are direct API (no MCP) and added via `create_cloudwatch_toolset(config)` in `engine/tools/cloudwatch.py`.

**Model provider routing** (`_get_model` in `orchestrator.py`). Accepts either `provider:model_id` (e.g. `bedrock:anthropic.claude-...`, `ollama:llama3`, `openrouter:...`) or a bare model id whose prefix is inferred: `claude*` → anthropic, `gpt*|o1|o3|o4` → openai, `gemini*` → google-gla, fallback → openai. Each branch pulls its key off `AgentSettings` and constructs the matching LangChain chat model. Bedrock uses `AWS_REGION`; Ollama points at `OLLAMA_HOST` via OpenAI-compatible endpoint.

**Settings load from the user config dir, not the repo root.** `settings/paths.py` resolves `platformdirs.user_config_dir("atomic-sre")/.env` and `engine/settings.py` points every `pydantic-settings` `SettingsConfigDict` at that path. The interactive setup wizard (`interfaces/setup/`) writes to this file. Editing `./.env` in the repo will be ignored unless you also `load_dotenv` it manually (`run.py` does this for the headless path). `GitHubSettings` and `SlackSettings` have required fields with no defaults — instantiating `get_settings()` without those env vars will raise.

**CLI surface.** `interfaces/main.py` is a Click group that, with no subcommand, calls `start_interactive_shell()`. The shell offers Local (`handlers/local.py`, runs `diagnose_error` in-process) and Remote Deployment (`handlers/remote/menu.py`, drives the AWS provisioning code under `infrastructure/aws/` — ECR push, IAM, security groups, ECS task creation, secrets, cleanup). The first-run wizard under `interfaces/setup/` collects API keys and writes the user `.env`.

**Adding a new tool/integration** (also documented in `DEVELOPMENT.md`): prefer an MCP server — add a `Connection` to the `connections` dict in `_load_mcp_tools` and, if needed, extend the allowlist in `_filter_mcp_tools`. For direct-API integrations, implement the relevant ABC in `engine/definitions.py` (`LoggingInterface`, `RepositoryInterface`, `MessagingInterface`) and expose `@tool`-decorated callables via a `create_*_toolset(config)` factory, mirroring `engine/tools/cloudwatch.py`.

## Project conventions (from AGENTS.md)

- UK English in code, comments, and docs. UK-vs-US-spelling false positives go in `typos.toml`.
- No em dashes in comments or documentation.
- Python 3.13 syntax even though `pyproject.toml` allows 3.12+ (matches the Dockerfile and ruff `target-version`).
- Google-style docstrings, single-line module/script top-level docstrings, no types in `Args:`.
- Mypy is `strict = true`; tests and `docs/` are excluded but `src/` is not.

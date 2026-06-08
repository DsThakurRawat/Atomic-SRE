# SPEC.md

Authoritative specification for **Atomic SRE** — a multi-agent orchestration engine that automates log triage, code-aware root-cause analysis, and human-in-the-loop remediation for Site Reliability Engineering. This document covers requirements, user-facing behaviour, technical architecture, and the public Python API and data models.

> Source of truth for behaviour: the code under `src/atomic_sre/`. If a divergence is found between this document and the code, the code wins and this document should be updated.

---

## 1. Requirements

### 1.1 Goals

- **Autonomous triage.** Given a CloudWatch log group, a service name, and a lookback window, produce a structured `ErrorDiagnosis` consisting of: summary, root cause, affected services, suggested fixes, and supporting log excerpts.
- **Code-aware diagnosis.** Pull relevant source context from GitHub on demand via MCP rather than indexing or cloning the whole repository.
- **Human-in-the-loop delivery.** Post the diagnosis into a Slack thread for review; never act on the fix automatically.
- **Provider neutrality on the LLM side.** Support Anthropic, OpenAI, Groq, Google Gemini, Ollama, OpenRouter, and AWS Bedrock through a single configuration knob (`MODEL`).
- **Two deployment shapes from one codebase.** Local interactive runs (CLI) and remote unattended runs (ECS task).
- **Measurable reasoning quality.** Ship evaluation harnesses for both tool-routing behaviour and final diagnosis quality.

### 1.2 Non-goals

- No automated commit, push, deploy, or rollback. The agent never mutates remote state beyond a single Slack post.
- No log indexing, log storage, or alert ingestion pipeline. CloudWatch is queried on demand per run.
- No GitHub write access. The GitHub MCP allowlist (see §3.4) is restricted to read tools (`search_code`, `get_file_contents`).
- No support for log sources other than CloudWatch in v0.2.x. Other providers are surfaced as planned via the `LoggingInterface` abstraction (§4.3).
- No GUI. The user interface is a `rich` + `questionary` CLI.

### 1.3 Constraints

- **Python:** `>=3.12,<4.0` per `pyproject.toml`; ruff and the Dockerfile target 3.13; UK English; Google-style docstrings; no em dashes (see `AGENTS.md`).
- **Runtime dependencies on external services:** AWS CloudWatch Logs (`logs:FilterLogEvents`), GitHub Copilot MCP (`https://api.githubcopilot.com/mcp/`), Slack MCP (`korotovsky/slack-mcp-server` on `:13080`), and one LLM provider.
- **Configuration location:** the runtime `.env` lives under `platformdirs.user_config_dir("atomic-sre")`, **not** the repo root. This is non-negotiable for the CLI path; the headless `run.py` happens to `load_dotenv` the same file.
- **State machine:** the agent must terminate. It does so only by emitting a valid `ErrorDiagnosis` tool call (§3.3); there is no max-iteration safety net beyond LangGraph defaults.

### 1.4 Success criteria

- A `diagnose_error(...)` call against a populated CloudWatch log group returns a Pydantic-validated `ErrorDiagnosis` with at least `summary` and `root_cause` populated.
- The Slack channel receives at least two messages: an "Anomaly detected" opener and a structured diagnosis reply threaded under it.
- Routing benchmark and diagnosis-quality benchmark suites run to completion against Opik and emit scores.

---

## 2. Functional specification

### 2.1 Trigger sources

| Source | Path | Notes |
| --- | --- | --- |
| Interactive CLI | `uv run atomic-sre` | Click group → `start_interactive_shell()` → Local handler → `diagnose_error(...)`. |
| Headless script | `uv run python -m atomic_sre.run <log_group> <service_name> [time_range_minutes]` | Args take precedence over `LOG_GROUP`, `SERVICE_NAME`, `TIME_RANGE_MINUTES` env vars. `time_range_minutes` defaults to 10. |
| Public API | `from atomic_sre import diagnose_error` | Documented in §4.1. |
| Containerised | `docker compose up -d` | Runs `python -m atomic_sre.run` as the entry CMD; reads env from compose. |

### 2.2 Operational modes

- **Local mode** (`interfaces/handlers/local.py`): LangGraph runs in-process on the developer's machine. CloudWatch and GitHub MCP are reached over the network; Slack MCP is typically the local Docker sidecar at `http://localhost:13080/sse`.
- **Remote Deployment mode** (`interfaces/handlers/remote/menu.py` + `infrastructure/aws/*`): the interactive shell provisions and runs the agent as an ECS task. The provisioning surface includes ECR push, IAM roles, VPC networking, security groups, secrets, ECS task definition + run, status polling, and cleanup.

### 2.3 Reasoning workflow (user-visible contract)

Enforced by the system prompt (`engine/prompts/system_prompt.txt`) and per-run prompt (`engine/prompts/diagnosis_prompt.txt`):

1. **Initialise Slack thread.** Call `conversations_add_message` with `channel_id` and an "Anomaly detected" payload. Capture the returned `ts`.
2. **Telemetry & source diagnosis.** Call `search_error_logs` for the configured log group, service, and window. For each notable error, cross-reference GitHub via `search_code` and `get_file_contents` scoped to `{owner}/{repo}@{ref}`.
3. **Publish atomic findings.** Call `conversations_add_message` again with the structured diagnosis, threaded under the captured `ts`. Emit `ErrorDiagnosis` to terminate the graph.

Failure modes called out in the system prompt:
- Slack `not_in_channel`: halt gracefully and prompt the user to `/invite` the bot.
- Zero anomalies: publish "No error logs found during the specified time window" and terminate.
- Hallucinated diagnoses without log evidence are prohibited by prompt.

### 2.4 CloudWatch query semantics

`engine/tools/cloudwatch.py::CloudWatchLogging.query_errors` issues a `filter_log_events` call with:

```
{ $.log_processed.severity = "error" && $.log_processed.service = "<service>" }
```

- Service name is escaped against `"` injection.
- Window is `[now - time_range_minutes, now]` in UTC.
- Result limit is **20 events** per call; entries are returned sorted descending by ISO timestamp.
- Logs must be structured JSON with `log_processed.severity` and `log_processed.service` fields. Non-JSON or differently-shaped logs will not match.

### 2.5 Supported integrations

| Category | Supported | Mechanism |
| --- | --- | --- |
| LLM | Anthropic, OpenAI, Groq, Google Gemini, Ollama, OpenRouter, AWS Bedrock | `_get_model` provider routing (§3.5). |
| Logs | AWS CloudWatch | Direct boto3 (`engine/tools/cloudwatch.py`). |
| Code | GitHub | MCP (`streamable_http` against the Copilot MCP). |
| Messaging | Slack | MCP (`sse` against `korotovsky/slack-mcp-server`), with a console-log fallback `@tool` if unreachable. |
| Deployment | Local Docker, AWS ECS | `docker-compose.yaml` for local; `infrastructure/aws/*` for ECS. |

### 2.6 Configuration surface

Loaded by `pydantic-settings` from `platformdirs.user_config_dir("atomic-sre")/.env`:

| Variable | Required? | Default | Used by |
| --- | --- | --- | --- |
| `MODEL` | No | `claude-sonnet-4-6` | `_get_model` provider routing. |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GROQ_API_KEY` / `GOOGLE_API_KEY` / `OPENROUTER_API_KEY` | One, matching the chosen `MODEL` | None | Same. |
| `OLLAMA_HOST` | No | `http://localhost:11434` | Ollama branch. |
| `AWS_REGION` | No | `eu-west-2` | CloudWatch + Bedrock. |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_SESSION_TOKEN` | Optional (boto3 default chain otherwise) | None | CloudWatch. |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | **Yes** | — | GitHub MCP auth. |
| `GITHUB_MCP_URL` | No | `https://api.githubcopilot.com/mcp/` | GitHub MCP transport. |
| `GITHUB_OWNER` / `GITHUB_REPO` / `GITHUB_REF` | **Yes** | — | Injected into the diagnosis prompt. |
| `SLACK_CHANNEL_ID` | **Yes** | — | Slack target channel. |
| `SLACK_MCP_URL` | No | `http://localhost:13080/sse` | Slack MCP transport. |
| `SLACK_BOT_TOKEN` | Yes (for the sidecar container) | — | Slack MCP authenticates with this; read by `docker-compose.yaml`, not by `AgentSettings`. |
| `OPIK_API_KEY` / `OPIK_WORKSPACE` | Only for tracing/eval | None | Benchmarks. |

Note: `GitHubSettings` and `SlackSettings` declare their required fields with no defaults — instantiating `get_settings()` without them raises `ValidationError`. The setup wizard (`interfaces/setup/wizard.py`) writes the file on first run.

### 2.7 Diagnosis output format

The terminal artefact is an `ErrorDiagnosis` (§4.2). The Slack post is a free-form Markdown rendering of that same content, composed by the LLM per the system prompt. Headless `run.py` prints `summary`, `root_cause`, and `suggested_fixes[].description` to stdout.

---

## 3. Technical architecture

### 3.1 Module layout

```
src/atomic_sre/
├── __init__.py              # Public API re-exports
├── run.py                   # Headless entrypoint
├── engine/
│   ├── orchestrator.py      # LangGraph StateGraph, model routing, MCP loading
│   ├── models.py            # Pydantic data models
│   ├── settings.py          # pydantic-settings (AgentSettings + sub-settings)
│   ├── definitions.py       # ABCs for non-MCP integrations
│   ├── prompts.py           # Template loader
│   ├── prompts/             # System and diagnosis prompt .txt files
│   └── tools/
│       └── cloudwatch.py    # boto3-based logging toolset
├── interfaces/
│   ├── main.py              # Click entrypoint
│   ├── interactive_shell.py # Top-level menu (Local / Remote / Exit)
│   ├── console/             # rich console, banner, ASCII art, styles
│   ├── setup/               # First-run wizard (questionary)
│   └── handlers/
│       ├── local.py         # Local diagnosis runner
│       └── remote/aws/ecs/  # ECS provisioning + run + cleanup menus
├── infrastructure/aws/      # ECR, IAM, secrets, network, SGs, ECS, status
├── settings/paths.py        # platformdirs user-config paths
└── benchmarks/
    ├── routing/             # Tool-call routing eval (Opik)
    ├── diagnostics/         # Diagnosis-quality eval (Opik)
    └── shared/case_loader.py
```

### 3.2 LangGraph state machine

`engine/orchestrator.py::build_agent_graph` compiles a `StateGraph[AgentState]` with two nodes and three edges:

```
       ┌──────────┐                       ┌─────────┐
START ─►   agent  ├── route_after_model ──►  tools  │
       │          ◄──────────────────────┤         │
       └────┬─────┘                       └─────────┘
            │ ErrorDiagnosis accepted
            ▼
           END
```

- **`AgentState`** is a `TypedDict` with `messages: Annotated[Sequence[BaseMessage], add_messages]` and `diagnosis: ErrorDiagnosis | None`.
- **`call_model`** node prepends `SystemMessage(SYSTEM_PROMPT)` if no system message is present, then invokes `model.bind_tools(tools + [ErrorDiagnosis])`.
- **`route_after_model`** terminates if `state["diagnosis"]` is set, routes to `tools` if the last message has `tool_calls`, sends the last `tool` message back to `agent`, and otherwise ends.
- **Termination** is the model emitting an `ErrorDiagnosis` tool call validated by `_handle_diagnosis_validation`. Multiple `ErrorDiagnosis` calls in the same turn are rejected with a `ToolMessage` instructing a single final call. `ValidationError`/`TypeError` cases produce a structured error message to enable a retry.

### 3.3 Tool sources

Tools are assembled by `create_atomic_sre(config)` in three layers:

1. **GitHub MCP** — `streamable_http` to `config.github.mcp_url` with `Authorization: Bearer {token}`.
2. **Slack MCP** — `sse` to `config.slack.mcp_url`.
3. **CloudWatch (direct)** — `create_cloudwatch_toolset(config)` builds a `@tool` wrapping `CloudWatchLogging.query_errors`.

`_filter_mcp_tools` enforces an allowlist:

- Slack: tool name must contain `conversations_add_message`. If no Slack tool registers, a fallback `@tool` is added that logs to console and returns a synthetic success payload.
- GitHub: tool name must contain `search_code` or `get_file_contents`.

MCP server failures are caught and logged at WARNING; the agent proceeds without those tools.

### 3.4 Validation gate for terminal output

`_handle_diagnosis_validation(response)`:

- Inspects `response.tool_calls`.
- If more than one `ErrorDiagnosis` tool call is present, all are rejected with `ToolMessage`s.
- The single `ErrorDiagnosis` call is constructed via `ErrorDiagnosis(**diag_call["args"])`. On success, the parsed object becomes `state["diagnosis"]` and all sibling tool calls receive accept/cancel `ToolMessage`s. On failure, errors are flattened to `loc: msg` strings and returned for retry.

### 3.5 Model provider routing

`_get_model(config)` accepts either `provider:model_id` or a bare model id whose prefix is matched against `_MODEL_PREFIX_MAP`:

| Prefix | Provider | Backing class |
| --- | --- | --- |
| `claude*` | `anthropic` | `langchain_anthropic.ChatAnthropic` |
| `gpt*`, `o1`, `o3`, `o4` | `openai` | `langchain_openai.ChatOpenAI` |
| `gemini*` | `google-gla` | `langchain_google_genai.ChatGoogleGenerativeAI` |
| explicit `bedrock:...` | `bedrock` | `langchain_aws.ChatBedrock` (region from `AWS_REGION`) |
| explicit `ollama:...` | `ollama` | `ChatOpenAI` against `{OLLAMA_HOST}/v1` |
| explicit `openrouter:...` | `openrouter` | `ChatOpenAI` against `https://openrouter.ai/api/v1` |
| explicit `groq:...` | `groq` | `langchain_groq.ChatGroq` |
| anything else | `openai` (fallback) | `ChatOpenAI` |

`_require_key` raises a `ValueError` with the offending env var name when the matching API key is missing.

### 3.6 Settings layering

`engine/settings.py` defines four `BaseSettings` classes, all pointing at `settings/paths.py::env_path()`:

- `AgentSettings` (LLM keys, `MODEL`, `OLLAMA_HOST`, plus required sub-settings).
- `AWSSettings` (env prefix `AWS_`).
- `GitHubSettings` (env prefix `GITHUB_`; `personal_access_token`, `owner`, `repo`, `ref` are required).
- `SlackSettings` (env prefix `SLACK_`; `channel_id` is required).

`get_settings()` constructs them explicitly. There is no `lru_cache` — each call re-reads the env.

### 3.7 Prompt construction

`engine/prompts.py` reads `system_prompt.txt` once at import time. `build_diagnosis_prompt(config, log_group, service_name, time_range_minutes)` `.format()`s the per-run template with `log_group`, `time_range_minutes`, `service_display`, `owner`, `repo`, `ref`, `channel_id`.

### 3.8 Adding new integrations

Two patterns, both documented in `DEVELOPMENT.md`:

1. **MCP server** — add a `Connection` entry to the `connections` dict in `_load_mcp_tools`. Extend the allowlist in `_filter_mcp_tools` if needed.
2. **Direct API** — implement the relevant ABC in `engine/definitions.py` (`LoggingInterface`, `RepositoryInterface`, or `MessagingInterface`), then expose `@tool` callables through a `create_<thing>_toolset(config)` factory in `engine/tools/`, mirroring `cloudwatch.py`. Wire the factory into `create_atomic_sre`.

### 3.9 Quality gates

| Tool | Config | Notes |
| --- | --- | --- |
| `ruff` (lint + format) | `ruff.toml`, `target-version = "py313"`, line-length 100, Google-style pydocstyle | Run via pre-commit. |
| `mypy` | `mypy.ini`, `strict = true`, `src` on `mypy_path`, excludes `tests/` and `docs/` | Run via pre-commit. |
| `typos` | `typos.toml` | UK English; add false positives there. |
| `bandit` | `bandit.yaml` | Security lint. |
| `trufflehog` | Docker, verified-secrets only, runs on `pre-commit` and `pre-push`. |
| `pytest` | `pyproject.toml::[tool.pytest.ini_options]`, `--cov=src` default | `tests/` only. |
| Benchmarks | `atomic-sre-run-tool-call-eval`, `atomic-sre-run-diagnosis-quality-eval` | Opik traces; datasets under `benchmarks/*/dataset`. |

### 3.10 CI

`.github/workflows/ci.yml` runs `pre-commit run --all-files` and `pytest tests` on `pull_request` and `push` to `main`/`develop` using `uv`. `publish.yml` handles releases. `scan-dependencies.yml` runs dependency scanning.

---

## 4. Public API and data models

The package's public surface is exactly what `atomic_sre/__init__.py` re-exports.

### 4.1 Functions

```python
async def diagnose_error(
    log_group: str,
    service_name: str,
    time_range_minutes: int = 10,
    config: AgentSettings | None = None,
) -> ErrorDiagnosis
```

End-to-end run. Loads settings if `config is None`, builds the agent, formats the diagnosis prompt, invokes the graph, and asserts the result contains a valid `ErrorDiagnosis`. Raises `RuntimeError("Agent failed to output a structured diagnosis.")` if the graph terminates without one.

```python
async def create_atomic_sre(
    config: AgentSettings,
) -> CompiledStateGraph[AgentState, Any, Any]
```

Lower-level constructor for callers who want to drive the graph manually (e.g. to inject extra tools, swap prompts, or stream intermediate state). Returns a compiled LangGraph graph whose state is `AgentState`.

```python
def get_settings() -> AgentSettings
```

Reads the user config `.env` and constructs the nested settings tree. Raises `pydantic.ValidationError` if required fields are missing.

### 4.2 Pydantic models

All are `pydantic.BaseModel` subclasses defined in `engine/models.py`.

```python
class LogEntry(BaseModel):
    timestamp: str        # ISO 8601 string (not datetime)
    message: str
    log_stream: str | None = None

class LogQueryResult(BaseModel):
    entries: list[LogEntry] = []
    log_group: str
    query: str            # The CloudWatch filter pattern that produced these entries

class SuggestedFix(BaseModel):
    description: str
    file_path: str | None = None
    code_snippet: str | None = None

class ErrorDiagnosis(BaseModel):
    summary: str
    root_cause: str
    affected_services: list[str] = []
    suggested_fixes: list[SuggestedFix] = []
    related_logs: list[str] = []
    timestamp: datetime = Field(default_factory=datetime.now)
```

`ErrorDiagnosis` is also `bind_tools`-ed onto the LLM as the structured termination signal (§3.4). The LLM "calls" it when ready to terminate; the validation gate inspects the call and either stores it or asks for a retry.

### 4.3 Internal interfaces (extensibility hooks)

`engine/definitions.py` defines three ABCs used by the direct-API extension pattern. They are intentionally **not** re-exported from the top-level package:

```python
class LoggingInterface(ABC):
    async def query_errors(
        self, source: str, service_name: str, time_range_minutes: int = 10,
    ) -> LogQueryResult: ...

class RepositoryInterface(ABC):
    async def get_file(self, repo: str, path: str, ref: str | None = None) -> str: ...

class MessagingInterface(ABC):
    async def send_message(self, channel: str, message: str) -> None: ...
```

`CloudWatchLogging` is the only concrete implementation in-tree. The GitHub and Slack interfaces exist for parity with planned non-MCP providers (GitLab, Bitbucket, Teams, PagerDuty).

### 4.4 Settings classes

`AgentSettings`, `AWSSettings`, `GitHubSettings`, `SlackSettings` (see §3.6). All four are `pydantic_settings.BaseSettings`. The user-facing variable surface is in §2.6.

### 4.5 CLI entry points

Declared in `pyproject.toml::[project.scripts]`:

| Script | Target | Purpose |
| --- | --- | --- |
| `atomic-sre` | `atomic_sre.interfaces.main:main` | Interactive CLI. |
| `atomic-sre-run-tool-call-eval` | `atomic_sre.benchmarks.routing.run:main` | Tool-routing benchmark. |
| `atomic-sre-run-diagnosis-quality-eval` | `atomic_sre.benchmarks.diagnostics.run:main` | Diagnosis-quality benchmark. |

---

## 5. Versioning and compatibility

- The project is at `0.2.1` (pre-1.0). Breaking changes to settings, the `AgentState` shape, and the `ErrorDiagnosis` schema are allowed between minor versions and should be called out in the changelog.
- The Python public surface (§4.1, §4.2) is what `atomic_sre/__init__.py` re-exports. Anything not in `__all__` is internal.
- The `MODEL` default tracks the most capable Anthropic Sonnet tier supported by the pinned LangChain integrations; bumping it counts as a behavioural change worth a release note.

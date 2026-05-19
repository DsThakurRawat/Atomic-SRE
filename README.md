<h1 align="center"> <!-- spellchecker:disable-line -->
    🚀 Atomic SRE 🕵️‍♀️
</h1>

<p align="center">
  <img src="docs/imgs/banner.png" alt="Atomic SRE Banner" width="800">
</p>

<p align="center">
    <strong>Flagship Orchestration Engine for the Autonomous Multi-Agent AI Organization</strong>
</p>

Welcome to **Atomic SRE**. This is a premium, open-source multi-agent orchestration engine designed to automate the heavy lifting of Site Reliability Engineering. It coordinates specialized autonomous agents to monitor logs, diagnose production issues, and execute root-cause fixes across distributed systems.

<p align="center"> <!-- spellchecker:disable-line -->
  <img src="docs/imgs/demo.gif" alt="flow" width="500">
</p>

# 🏃 Quick Start

## Prerequisites

- Python 3.13+
- [Docker](https://docs.docker.com/get-docker/) (required for local mode)

## 1️⃣ Install Atomic SRE
```bash
pip install atomic-sre
```

## 2️⃣ Start the CLI
```bash
atomic-sre
```

On first run, the setup wizard will guide you through configuration:

![cli-setup](docs/imgs/cli-setup.png)

## 3️⃣ Provide the required setup values

The wizard currently asks for:

- `ANTHROPIC_API_KEY`
- `GITHUB_PERSONAL_ACCESS_TOKEN`
- `GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_REF`
- `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`
- AWS credentials (`AWS_PROFILE` or access keys) and `AWS_REGION`

By default the agent uses `claude-sonnet-4-5-20250929`. You can override this by setting the `MODEL` environment variable.

## 4️⃣ Pick a running mode

After setup, the CLI gives you two modes:

- `Local`: run diagnoses from your machine against a CloudWatch log group.
- `Remote Deployment`: deploy and run the agent on AWS ECS.

Remote mode currently supports AWS ECS only for deploying the agent runtime.

This is the local shell view:

![cli-home](docs/imgs/cli-home.png)

# 🌟 What Does It Do?

Think about a microservice app where any service can fail at any time. **Atomic SRE** watches error logs, identifies which service is affected, checks the configured GitHub repository, diagnoses likely root causes, suggests fixes, and reports back to Slack.

In short, it handles the heavy lifting so your team can focus on fixing the issue quickly.

Your application can run on Kubernetes, ECS, VMs, or elsewhere. The key requirement is that logs are available in CloudWatch.

# 🏛️ Architecture

Atomic SRE operates as a sophisticated state machine, coordinating between logging platforms, source code repositories, and communication channels.

```mermaid
graph TD
    A[CloudWatch Logs] --> B{Atomic SRE}
    B --> C[GitHub MCP]
    C --> B
    B --> D[Diagnosis & Fix Suggestions]
    D --> E[Slack Notification]
    
    subgraph "Core Agent Loop"
    B
    C
    end
```

### High-Level Flow

1. **Observe**: Read error logs from CloudWatch.
2. **Reason**: Identify the service and context.
3. **Act**: Inspect source code via the GitHub MCP integration.
4. **Diagnose**: Produce high-fidelity diagnosis and fix suggestions.
5. **Report**: Send results to Slack for human review.

```mermaid
graph LR
    subgraph "High-Level SRE Flow"
        1[Observe] -->|Read Logs| 2[Reason]
        2 -->|Identify Service| 3[Act]
        3 -->|Inspect GitHub MCP| 4[Diagnose]
        4 -->|Create Fix Suggestions| 5[Report]
        5 -->|Notify Slack| End([Review])
    end

    style 1 fill:#22C55E,stroke:#15803D,stroke-width:2px,color:#fff
    style 2 fill:#22C55E,stroke:#15803D,stroke-width:2px,color:#fff
    style 3 fill:#22C55E,stroke:#15803D,stroke-width:2px,color:#fff
    style 4 fill:#22C55E,stroke:#15803D,stroke-width:2px,color:#fff
    style 5 fill:#22C55E,stroke:#15803D,stroke-width:2px,color:#fff
    style End fill:#15803D,stroke:#166534,stroke-width:2px,color:#fff
```

# 🛠️ Technology Stack

Atomic SRE is built using modern, production-ready AI agent frameworks:

- **Core Runtime**: Python 3.13+
- **Agent Orchestration**: [LangChain](https://github.com/langchain-ai/langchain) & [LangGraph](https://github.com/langchain-ai/langgraph) / [Deep Agents](https://github.com/langchain-ai/deepagents)
- **MCP Client**: `MultiServerMCPClient` (from `langchain-mcp-adapters`) for dynamic tool invocation
- **Evaluation & Tracing**: [Opik](https://github.com/comet-ml/opik) for automated span/trace capturing and dataset generation
- **Logging & Infrastructure**: AWS CloudWatch (Logs client), Docker
- **Remote Orchestration**: AWS ECS (deployment environment)

# 🗺️ Integration Roadmap

#### 🧠 Model provider

- [x] Anthropic
- [ ] vLLM
- [ ] OpenAI

#### 🪵 Logging platform

- [x] AWS CloudWatch
- [ ] Google Cloud Observability
- [ ] Azure Monitor

#### 🏢 Remote code repository

- [x] GitHub
- [ ] GitLab
- [ ] Bitbucket

#### 🔔 Notification channel

- [x] Slack
- [ ] Microsoft Teams

#### 🕶️ Remote deployment mode:

- [x] AWS ECS

> [!TIP]
> Looking for a feature or integration that is not listed yet? Open a [Feature / Integration request](https://github.com/DsThakurRawat/Atomic-SRE/issues/new?template=feature_or_integration_request.yml) 🚀

# 🧪 Evaluation

We built a comprehensive evaluation suite to test both tool-use behaviour and diagnosis quality.

- [Evaluation overview](src/atomic_sre/eval/README.md)
- [Tool call evaluation](src/atomic_sre/eval/tool_call/README.md)
- [Diagnosis quality evaluation](src/atomic_sre/eval/diagnosis_quality/README.md)

Run the suites with:

```bash
uv run atomic-sre-run-tool-call-eval
uv run atomic-sre-run-diagnosis-quality-eval
```

# 🤔 Why We Built This

We wanted to learn practical best practices for running AI agents in production: cost, safety, observability, and evaluation. We are sharing the journey in the open and publishing what we learn as we go.

We also write about this work on the [DIVYANSH RAWAT blog](https://www.DsThakurRawat.ai/blog).

> **Contributions welcome.** [Join us](CONTRIBUTING.md) and help shape the future of AI-powered SRE.

# 🔧 For Developers

See [DEVELOPMENT.md](DEVELOPMENT.md) for the full local setup guide.

Install dependencies:

```bash
uv sync --dev
```

Run the interactive CLI locally:

```bash
uv run atomic-sre
```

If you want to run a direct diagnosis without the CLI:

```bash
docker compose up -d slack
uv run python -m atomic_sre.run /aws/containerinsights/no-loafers-for-you/application currencyservice 10
```

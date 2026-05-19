# DEVELOPER README

This document is for developers of agentic-sre, specifically for v0.2.0.

## To start the agent

Run the CLI once and complete the configuration wizard to create the user `.env` file in the platform config directory.

Start the agent server and the Slack MCP server:
```bash
docker compose up -d
```

Trigger an error on the [store](http://aea33d77009704f67b39fe82a5c41aab-398063840.eu-west-2.elb.amazonaws.com/) by adding loaf to the cart, or change the currency from EUR to GBP. (Note, there is an bug that errors might take some time to be indexed so if you trigger the agent immediately after you cause an error it might not be able to find the log.)

Trigger the locally running agent:
```bash
uv run python -m agentic_sre.run /aws/containerinsights/no-loafers-for-you/application cartservice
```

Or:
```bash
uv run python -m agentic_sre.run /aws/containerinsights/no-loafers-for-you/application currencyservice
```

## Adding a New Tool

When adding a new tool/integration, follow one of these patterns:

### Option 1: MCP Server

If an MCP server exists for the service, you can configure it inside the `connections` dictionary in `agent.py` to be loaded dynamically by `MultiServerMCPClient`.

```python
# In src/agentic_sre/core/agent.py:
connections = {
    "example": {
        "transport": "stdio",  # or "sse" / "streamable_http"
        "command": "docker",
        "args": ["run", "-i", "--rm", "-e", f"TOKEN={config.example.token}", "mcp/example"],
    }
}
```

### Option 2: Direct API

Use this when no MCP server is available. You must implement the relevant interface and register the tool using standard LangChain `@tool` decoration.

```python
# tools/example.py
from langchain_core.tools import tool
from agentic_sre.core.interfaces import LoggingInterface
from agentic_sre.core.models import LogQueryResult
from agentic_sre.core.settings import AgentSettings

class ExampleLogging(LoggingInterface):
    async def query_errors(
        self,
        source: str,
        service_name: str,
        time_range_minutes: int = 10,
    ) -> LogQueryResult:
        # Implementation using direct API calls
        ...

def create_example_toolset(config: AgentSettings) -> list:
    impl = ExampleLogging(config.example.api_key)

    @tool
    async def search_logs(
        log_group: str,
        service_name: str,
        time_range_minutes: int = 10,
    ) -> LogQueryResult:
        """Search logs for errors."""
        return await impl.query_errors(log_group, service_name, time_range_minutes)

    return [search_logs]
```

**Examples:** `cloudwatch.py`

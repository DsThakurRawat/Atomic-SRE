"""GitHub MCP toolset construction for tool call evaluation."""

import os
from typing import Any

import opik
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


async def build_github_toolset() -> list[BaseTool]:
    """Build a real GitHub MCP toolset.

    Returns:
        A list of GitHub MCP tools.
    """
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        msg = (
            "Missing GitHub MCP configuration. "
            "Set GITHUB_PERSONAL_ACCESS_TOKEN before running tool-call eval."
        )
        raise RuntimeError(msg)

    connections: dict[str, Any] = {
        "github": {
            "transport": "streamable_http",
            "url": "https://api.githubcopilot.com/mcp/",
            "headers": {"Authorization": f"Bearer {token}"},
        }
    }

    client = MultiServerMCPClient(connections)  # type: ignore[arg-type]
    all_tools = await client.get_tools()

    allowed_github_tools = {"search_code", "get_file_contents"}
    tools = [t for t in all_tools if any(allowed in t.name for allowed in allowed_github_tools)]

    for tool in tools:
        coroutine = getattr(tool, "coroutine", None)
        func = getattr(tool, "func", None)

        if coroutine:
            orig_coro = coroutine

            async def wrapped_coro(
                *args: Any,
                orig_coro: Any = orig_coro,
                tool_name: str = tool.name,
                **kwargs: Any,
            ) -> Any:
                raw_args = kwargs or (args[0] if args else {})
                with opik.start_as_current_span(
                    name=tool_name,
                    type="tool",
                    input=raw_args if isinstance(raw_args, dict) else {},
                    metadata={"provider": "github_mcp", "mocked": False},
                ):
                    return await orig_coro(*args, **kwargs)

            tool.coroutine = wrapped_coro  # type: ignore[attr-defined]
        elif func:
            orig_func = func

            def wrapped_func(
                *args: Any,
                orig_func: Any = orig_func,
                tool_name: str = tool.name,
                **kwargs: Any,
            ) -> Any:
                raw_args = kwargs or (args[0] if args else {})
                with opik.start_as_current_span(
                    name=tool_name,
                    type="tool",
                    input=raw_args if isinstance(raw_args, dict) else {},
                    metadata={"provider": "github_mcp", "mocked": False},
                ):
                    return orig_func(*args, **kwargs)

            tool.func = wrapped_func  # type: ignore[attr-defined]

    return tools

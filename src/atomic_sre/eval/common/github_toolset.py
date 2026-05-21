"""GitHub MCP toolset construction for evaluations."""

import os
from typing import Any, cast

import opik
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


async def build_github_toolset() -> list[BaseTool]:
    """Build a real GitHub MCP toolset for evaluation.

    Returns:
        A list of GitHub MCP tools.
    """
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")

    if not token:
        msg = (
            "Missing GitHub MCP configuration. "
            "Set GITHUB_PERSONAL_ACCESS_TOKEN before running evaluations."
        )
        raise RuntimeError(msg)

    connections = {
        "github": {
            "transport": "streamable_http",
            "url": "https://api.githubcopilot.com/mcp/",
            "headers": {"Authorization": f"Bearer {token}"},
        }
    }

    client = MultiServerMCPClient(connections)
    all_tools = cast(list[BaseTool], await client.get_tools())

    allowed_github_tools = {"search_code", "get_file_contents"}
    tools = [t for t in all_tools if any(allowed in t.name for allowed in allowed_github_tools)]

    for tool in tools:
        coroutine = getattr(tool, "coroutine", None)
        func = getattr(tool, "func", None)

        if coroutine:
            tool.coroutine = _make_traced_coro(coroutine, tool.name)  # type: ignore[attr-defined]
        elif func:
            tool.func = _make_traced_func(func, tool.name)  # type: ignore[attr-defined]

    return tools


def _make_traced_coro(coro: Any, name: str) -> Any:
    """Create an async wrapper that adds an Opik span around a coroutine."""

    async def wrapped(*args: Any, **kwargs: Any) -> Any:
        raw_args = kwargs or (args[0] if args else {})
        with opik.start_as_current_span(
            name=name,
            type="tool",
            input=raw_args if isinstance(raw_args, dict) else {},
            metadata={"provider": "github_mcp", "mocked": False},
        ):
            return await coro(*args, **kwargs)

    return wrapped


def _make_traced_func(func: Any, name: str) -> Any:
    """Create a sync wrapper that adds an Opik span around a function."""

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        raw_args = kwargs or (args[0] if args else {})
        with opik.start_as_current_span(
            name=name,
            type="tool",
            input=raw_args if isinstance(raw_args, dict) else {},
            metadata={"provider": "github_mcp", "mocked": False},
        ):
            return func(*args, **kwargs)

    return wrapped

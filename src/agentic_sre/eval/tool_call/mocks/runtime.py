"""Runtime state for tool call mocked tools."""

from dataclasses import dataclass

from agentic_sre.eval.tool_call.dataset.schema import ToolCallEvalCase


@dataclass
class MockToolRuntime:
    """Runtime state for one eval case."""

    case: ToolCallEvalCase

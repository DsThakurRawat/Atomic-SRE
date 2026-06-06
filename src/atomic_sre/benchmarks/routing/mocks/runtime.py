"""Runtime state for tool call mocked tools.

This module defines the Opik-based evaluation suites used to empirically measure the reliability,
diagnostic precision, and tool-routing accuracy of the Atomic-SRE agent.
"""

from dataclasses import dataclass

from atomic_sre.benchmarks.routing.dataset.schema import ToolCallEvalCase


@dataclass
class MockToolRuntime:
    """Runtime state for one eval case."""

    case: ToolCallEvalCase

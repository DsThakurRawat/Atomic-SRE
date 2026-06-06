"""Mock tools for diagnosis quality evaluation.

This module defines the Opik-based evaluation suites used to empirically measure the reliability,
diagnostic precision, and tool-routing accuracy of the Atomic-SRE agent.
"""

from atomic_sre.benchmarks.diagnostics.mocks.runtime import MockToolRuntime
from atomic_sre.benchmarks.diagnostics.mocks.toolset import build_mock_toolset

__all__ = [
    "MockToolRuntime",
    "build_mock_toolset",
]

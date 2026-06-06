"""Runtime state for diagnosis quality mocked tools.

This module defines the Opik-based evaluation suites used to empirically measure the reliability,
diagnostic precision, and tool-routing accuracy of the Atomic-SRE agent.
"""

from dataclasses import dataclass

from atomic_sre.benchmarks.diagnostics.dataset.schema import DiagnosisQualityEvalCase


@dataclass
class MockToolRuntime:
    """Runtime state for one eval case."""

    case: DiagnosisQualityEvalCase

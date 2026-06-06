"""Dataset for tool call evaluation.

This module defines the Opik-based evaluation suites used to empirically measure the reliability,
diagnostic precision, and tool-routing accuracy of the Atomic-SRE agent.
"""

from atomic_sre.benchmarks.routing.dataset.create_and_populate import (
    DEFAULT_DATASET_NAME,
    create_and_populate_dataset,
)
from atomic_sre.benchmarks.routing.dataset.schema import ToolCallEvalCase

__all__ = ["create_and_populate_dataset", "ToolCallEvalCase", "DEFAULT_DATASET_NAME"]

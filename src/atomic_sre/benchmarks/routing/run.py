"""Run tool call evaluation.

This module defines the Opik-based evaluation suites used to empirically measure the reliability,
diagnostic precision, and tool-routing accuracy of the Atomic-SRE agent.
"""

from atomic_sre.benchmarks.routing.config import DEFAULT_EXPERIMENT_NAME
from atomic_sre.benchmarks.routing.dataset.create_and_populate import DEFAULT_DATASET_NAME
from atomic_sre.benchmarks.routing.experiment import run_experiment


def main() -> None:
    """Run tool call evaluation with default configuration."""
    try:
        result = run_experiment()
    except ValueError as exc:
        print("Model configuration error for eval run.")
        print("Set MODEL and the matching provider API key before running the eval.")
        raise SystemExit(1) from exc
    except RuntimeError as exc:
        print(str(exc))
        raise SystemExit(1) from exc

    test_results = getattr(result, "test_results", None) or getattr(result, "testResults", [])
    print(f"Experiment: {DEFAULT_EXPERIMENT_NAME}")
    print(f"Dataset: {DEFAULT_DATASET_NAME}")
    print(f"Cases evaluated: {len(test_results)}")


if __name__ == "__main__":
    main()

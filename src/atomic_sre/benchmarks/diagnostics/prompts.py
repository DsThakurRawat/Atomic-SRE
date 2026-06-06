"""Prompt rendering for diagnosis quality evaluation.

This module defines the Opik-based evaluation suites used to empirically measure the reliability,
diagnostic precision, and tool-routing accuracy of the Atomic-SRE agent.
"""

from atomic_sre.benchmarks.diagnostics.config import (
    DEFAULT_SLACK_CHANNEL_ID,
    DEFAULT_TIME_RANGE_MINUTES,
)
from atomic_sre.benchmarks.diagnostics.dataset.schema import DiagnosisQualityEvalCase
from atomic_sre.engine.prompts import DIAGNOSIS_PROMPT_TEMPLATE


def render_agent_prompt(case: DiagnosisQualityEvalCase) -> str:
    """Render diagnosis prompt with fixed GitHub scope context.

    Args:
        case: The case to run.

    Returns:
        The diagnosis prompt.
    """
    prompt = DIAGNOSIS_PROMPT_TEMPLATE.format(
        log_group=case.log_group,
        time_range_minutes=DEFAULT_TIME_RANGE_MINUTES,
        service_display=case.service_name,
        owner=case.github_owner,
        repo=case.github_repo,
        ref=case.github_ref,
        channel_id=DEFAULT_SLACK_CHANNEL_ID,
    )

    return prompt

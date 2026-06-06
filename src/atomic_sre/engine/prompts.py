"""System prompts for the Atomic SRE.

This module encapsulates the core LangGraph orchestrator, agent state machines, and LLM
definitions for Atomic-SRE. It drives the core reasoning loop and dynamic tool selection.
"""

from pathlib import Path

from atomic_sre.engine.settings import AgentSettings

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt from a text file."""
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


SYSTEM_PROMPT = _load_prompt("system_prompt.txt")
DIAGNOSIS_PROMPT_TEMPLATE = _load_prompt("diagnosis_prompt.txt")


def build_diagnosis_prompt(
    config: AgentSettings,
    log_group: str,
    service_name: str,
    time_range_minutes: int = 10,
) -> str:
    """Build a diagnosis prompt for the agent."""
    prompt = DIAGNOSIS_PROMPT_TEMPLATE.format(
        log_group=log_group,
        time_range_minutes=time_range_minutes,
        service_display=service_name,
        owner=config.github.owner,
        repo=config.github.repo,
        ref=config.github.ref,
        channel_id=config.slack.channel_id,
    )

    return prompt

"""Tool call evaluation experiment."""

import asyncio
from typing import Any

import opik
from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.evaluation_result import EvaluationResult

from atomic_sre.core.models import ErrorDiagnosis
from atomic_sre.core.prompts import SYSTEM_PROMPT
from atomic_sre.eval.tool_call.config import (
    DEFAULT_EXPERIMENT_NAME,
    DEFAULT_MODEL,
    DEFAULT_OPIK_PROJECT_NAME,
)
from atomic_sre.eval.tool_call.dataset.create_and_populate import (
    DEFAULT_DATASET_NAME,
    create_and_populate_dataset,
)
from atomic_sre.eval.tool_call.dataset.schema import ToolCallEvalCase
from atomic_sre.eval.tool_call.github_toolset import build_github_toolset
from atomic_sre.eval.tool_call.metrics.expected_tool_select_order import (
    ExpectedToolSelectOrder,
)
from atomic_sre.eval.tool_call.metrics.expected_tool_selection import ExpectedToolSelection
from atomic_sre.eval.tool_call.mocks import MockToolRuntime, build_mock_toolset
from atomic_sre.eval.tool_call.prompts import render_agent_prompt


def evaluation_task(dataset_item: dict[str, Any]) -> dict[str, Any]:
    """Run one tool call case through the agent loop.

    Args:
        dataset_item: The dataset item to run.

    Returns:
        The task output dictionary for Opik scoring.
    """
    payload = dict(dataset_item)
    payload.pop("id", None)
    case = ToolCallEvalCase.model_validate(payload)
    return asyncio.run(run_case(case))


def run_experiment(dataset_name: str = DEFAULT_DATASET_NAME) -> EvaluationResult:
    """Run the tool call evaluation in local mode.

    Args:
        dataset_name: The name of the dataset to run.

    Returns:
        The evaluation result.
    """
    opik.config.update_session_config("project_name", DEFAULT_OPIK_PROJECT_NAME)
    opik.configure(use_local=True)
    client = Opik(project_name=DEFAULT_OPIK_PROJECT_NAME)
    dataset, _ = create_and_populate_dataset(client=client, dataset_name=dataset_name)

    return evaluate(
        dataset=dataset,
        task=evaluation_task,
        scoring_metrics=[ExpectedToolSelectOrder(), ExpectedToolSelection()],
        experiment_name=DEFAULT_EXPERIMENT_NAME,
        project_name=DEFAULT_OPIK_PROJECT_NAME,
        experiment_config={
            "suite": "tool_call",
            "dataset": dataset_name,
            "mode": "local",
            "model": DEFAULT_MODEL,
            "github_mode": "real_mcp",
            "cloudwatch_mode": "mock",
            "slack_mode": "mock",
        },
    )


async def run_case(case: ToolCallEvalCase) -> dict[str, Any]:
    """Execute one case using a real agent with hybrid toolsets.

    Args:
        case: The case to run.

    Returns:
        An empty dictionary, we will extract tool usage from the span tree.
    """
    runtime = MockToolRuntime(case)
    github_tools = await build_github_toolset()
    mock_tools = build_mock_toolset(runtime)

    tools = []
    tools.extend(mock_tools)
    tools.extend(github_tools)

    from deepagents import create_deep_agent

    from atomic_sre.core.agent import _get_model
    from atomic_sre.core.settings import get_settings

    config = get_settings()
    config.model = DEFAULT_MODEL
    model = _get_model(config)

    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        response_format=ErrorDiagnosis,
    )

    await agent.ainvoke({"messages": [{"role": "user", "content": render_agent_prompt(case)}]})
    return {}

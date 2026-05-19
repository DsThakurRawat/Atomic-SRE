"""Mock toolset builder for diagnosis quality evaluation."""

from typing import Any

from langchain_core.tools import BaseTool, tool

from agentic_sre.core.models import LogQueryResult
from agentic_sre.eval.diagnosis_quality.mocks import cloudwatch as cloudwatch_mocks
from agentic_sre.eval.diagnosis_quality.mocks import slack as slack_mocks
from agentic_sre.eval.diagnosis_quality.mocks.runtime import MockToolRuntime


def build_mock_toolset(runtime: MockToolRuntime) -> list[BaseTool]:
    """Build mocked Slack and CloudWatch toolset.

    Args:
        runtime: The mock tool runtime.

    Returns:
        List of mocked tools.
    """

    @tool
    async def conversations_add_message(
        channel_id: str,
        payload: str,
        thread_ts: str | None = None,
    ) -> dict[str, Any]:
        """Mock Slack message posting."""
        return await slack_mocks.conversations_add_message(
            channel_id,
            payload,
            thread_ts,
        )

    @tool
    async def search_error_logs(
        log_group: str,
        service_name: str,
        time_range_minutes: int = 10,
    ) -> LogQueryResult:
        """Mock CloudWatch error search."""
        return await cloudwatch_mocks.search_error_logs(
            runtime,
            log_group,
            service_name,
            time_range_minutes,
        )

    return [conversations_add_message, search_error_logs]

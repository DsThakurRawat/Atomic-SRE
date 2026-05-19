"""Agentic SRE using deepagents and LangChain."""

from typing import Any, cast

from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from agentic_sre.core.models import ErrorDiagnosis
from agentic_sre.core.prompts import SYSTEM_PROMPT, build_diagnosis_prompt
from agentic_sre.core.settings import AgentSettings, get_settings
from agentic_sre.core.tools import create_cloudwatch_toolset


def _get_model(config: AgentSettings) -> BaseChatModel:
    """Resolve the LangChain model object from configuration.

    Args:
        config: Agent settings.

    Returns:
        The resolved chat model.
    """
    model_id = config.model

    # Handle Ollama specifically for the host URL
    if model_id.startswith("ollama:"):
        base_id = model_id.replace("ollama:", "")
        return cast(
            BaseChatModel,
            ChatOpenAI(
                model=base_id,
                base_url=f"{config.ollama_host}/v1",
                api_key=SecretStr("ollama"),
            ),
        )

    # Handle Bedrock specifically for the region
    if model_id.startswith("bedrock:"):
        base_id = model_id.replace("bedrock:", "")
        return cast(
            BaseChatModel,
            ChatBedrock(
                model_id=base_id,
                region_name=config.aws.region,
            ),
        )

    # Handle Anthropic specifically
    if model_id.startswith("claude-"):
        api_key = SecretStr(config.anthropic_api_key or "")
        return cast(
            BaseChatModel,
            ChatAnthropic(
                model=model_id,  # type: ignore[call-arg]
                api_key=api_key,
            ),
        )

    # Default to OpenAI
    api_key = SecretStr(config.openai_api_key or "")
    return cast(
        BaseChatModel,
        ChatOpenAI(
            model=model_id,
            api_key=api_key,
        ),
    )


async def create_agentic_sre(config: AgentSettings) -> Any:
    """Create the Agentic SRE with all toolsets configured.

    Args:
        config: Agent settings.

    Returns:
        The compiled deep agent.
    """
    connections = {}
    if config.github.mcp_url:
        connections["github"] = {
            "transport": "streamable_http",
            "url": config.github.mcp_url,
            "headers": {"Authorization": f"Bearer {config.github.personal_access_token}"},
        }
    if config.slack.mcp_url:
        connections["slack"] = {
            "transport": "sse",
            "url": config.slack.mcp_url,
        }

    mcp_tools = []
    if connections:
        client = MultiServerMCPClient(connections)
        mcp_tools = await client.get_tools()

    allowed_slack_tools = {"conversations_add_message"}
    filtered_tools: list[BaseTool] = []
    for tool in mcp_tools:
        if "slack" in tool.name:
            if any(allowed in tool.name for allowed in allowed_slack_tools):
                filtered_tools.append(tool)
        else:
            filtered_tools.append(tool)

    cw_toolset = create_cloudwatch_toolset(config)
    filtered_tools.extend(cw_toolset)

    return create_deep_agent(
        model=_get_model(config),
        tools=filtered_tools,
        system_prompt=SYSTEM_PROMPT,
        response_format=ErrorDiagnosis,
    )


async def diagnose_error(
    log_group: str,
    service_name: str,
    time_range_minutes: int = 10,
    config: AgentSettings | None = None,
) -> ErrorDiagnosis:
    """Run a diagnosis for errors in a specific log group.

    Args:
        log_group: CloudWatch log group to analyse.
        service_name: Service name to filter.
        time_range_minutes: How far back to look for errors.
        config: Optional agent configuration.

    Returns:
        ErrorDiagnosis with findings and suggested fixes.
    """
    if config is None:
        config = get_settings()

    agent = await create_agentic_sre(config)
    prompt = build_diagnosis_prompt(config, log_group, service_name, time_range_minutes)

    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})

    diagnosis = result.get("response_format")
    if not isinstance(diagnosis, ErrorDiagnosis):
        raise RuntimeError("Agent failed to output a structured diagnosis.")

    return diagnosis

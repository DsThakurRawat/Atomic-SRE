"""Atomic SRE using deepagents and LangChain."""

import logging
from typing import Any, cast

from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from atomic_sre.core.models import ErrorDiagnosis
from atomic_sre.core.prompts import SYSTEM_PROMPT, build_diagnosis_prompt
from atomic_sre.core.settings import AgentSettings, get_settings
from atomic_sre.core.tools import create_cloudwatch_toolset

logger = logging.getLogger(__name__)


def _get_model(config: AgentSettings) -> BaseChatModel:
    """Resolve the LangChain model object from configuration.

    Args:
        config: Agent settings.

    Returns:
        The resolved chat model.
    """
    model_id = config.model
    provider = "openai"
    base_model = model_id

    if ":" in model_id:
        provider, base_model = model_id.split(":", 1)

    model_obj: BaseChatModel

    # Resolve based on provider name
    if provider == "ollama":
        model_obj = cast(
            BaseChatModel,
            ChatOpenAI(
                model=base_model,
                base_url=f"{config.ollama_host}/v1",
                api_key=SecretStr("ollama"),
            ),
        )
    elif provider == "bedrock":
        model_obj = cast(
            BaseChatModel,
            ChatBedrock(
                model_id=base_model,
                region_name=config.aws.region,
            ),
        )
    elif provider == "anthropic":
        api_key = SecretStr(config.anthropic_api_key or "")
        model_obj = cast(
            BaseChatModel,
            ChatAnthropic(
                model_name=base_model,
                api_key=api_key,
                timeout=None,
                stop=None,
            ),
        )
    elif provider == "groq":
        from langchain_groq import ChatGroq

        api_key = SecretStr(config.groq_api_key or "")
        model_obj = cast(
            BaseChatModel,
            ChatGroq(
                model=base_model,
                api_key=api_key,
            ),
        )
    elif provider == "google-gla":
        from langchain_google_genai import ChatGoogleGenerativeAI

        api_key = SecretStr(config.google_api_key or "")
        model_obj = cast(
            BaseChatModel,
            ChatGoogleGenerativeAI(
                model=base_model,
                google_api_key=api_key,
            ),
        )
    elif provider == "openrouter":
        api_key = SecretStr(config.openrouter_api_key or "")
        model_obj = cast(
            BaseChatModel,
            ChatOpenAI(
                model=base_model,
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            ),
        )
    else:
        # Default to OpenAI
        api_key = SecretStr(config.openai_api_key or "")
        model_obj = cast(
            BaseChatModel,
            ChatOpenAI(
                model=base_model,
                api_key=api_key,
            ),
        )

    return model_obj


async def _load_mcp_tools(config: AgentSettings) -> list[BaseTool]:
    """Load tools dynamically from Slack and GitHub MCP servers.

    Args:
        config: Agent settings.

    Returns:
        List of loaded MCP tools.
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

    mcp_tools: list[BaseTool] = []
    for name, conn in connections.items():
        try:
            client = MultiServerMCPClient({name: conn})
            tools = cast(list[BaseTool], await client.get_tools())
            mcp_tools.extend(tools)
        except Exception as e:
            logger.warning(f"Could not connect to {name} MCP server: {e}. Skipping {name} tools.")
    return mcp_tools


def _filter_mcp_tools(mcp_tools: list[BaseTool]) -> tuple[list[BaseTool], bool]:
    """Filter MCP tools to keep only essential Slack/GitHub tools.

    Args:
        mcp_tools: Unfiltered MCP tools.

    Returns:
        Tuple of filtered tools and whether Slack tool was registered.
    """
    allowed_slack_tools = {"conversations_add_message"}
    allowed_github_tools = {"search_code", "get_file_contents"}
    filtered_tools: list[BaseTool] = []
    has_slack = False

    for tool_obj in mcp_tools:
        if "slack" in tool_obj.name:
            if any(allowed in tool_obj.name for allowed in allowed_slack_tools):
                filtered_tools.append(tool_obj)
                has_slack = True
        elif any(allowed in tool_obj.name for allowed in allowed_github_tools):
            filtered_tools.append(tool_obj)
    return filtered_tools, has_slack


async def create_atomic_sre(config: AgentSettings) -> Any:
    """Create the Atomic SRE with all toolsets configured.

    Args:
        config: Agent settings.

    Returns:
        The compiled deep agent.
    """
    mcp_tools = await _load_mcp_tools(config)
    filtered_tools, has_slack = _filter_mcp_tools(mcp_tools)

    # Register fallback Slack tool if the MCP server is down or unconfigured
    if not has_slack:

        @tool
        async def conversations_add_message(
            channel_id: str,
            payload: str,
            thread_ts: str | None = None,
        ) -> dict[str, Any]:
            """Post message to Slack. Used for starting and posting final findings."""
            logger.warning(
                f"[Fallback Slack] Post to channel {channel_id}: {payload} (thread: {thread_ts})"
            )
            return {"status": "ok", "message": "Logged to console (Slack MCP unavailable)"}

        filtered_tools.append(conversations_add_message)

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

    agent = await create_atomic_sre(config)
    prompt = build_diagnosis_prompt(config, log_group, service_name, time_range_minutes)

    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})

    diagnosis = result.get("response_format")
    if not isinstance(diagnosis, ErrorDiagnosis):
        raise RuntimeError("Agent failed to output a structured diagnosis.")

    return diagnosis

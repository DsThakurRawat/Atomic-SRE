"""Agentic SRE using pydantic-ai."""

from pydantic_ai import Agent, models
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider

from agentic_sre.core.models import ErrorDiagnosis
from agentic_sre.core.prompts import SYSTEM_PROMPT, build_diagnosis_prompt
from agentic_sre.core.settings import AgentSettings, get_settings
from agentic_sre.core.tools import (
    create_cloudwatch_toolset,
    create_github_mcp_toolset,
    create_slack_mcp_toolset,
)


def _get_model(config: AgentSettings):
    """Resolve the pydantic-ai model object from configuration."""
    model_id = config.model
    
    # Handle Ollama specifically for the host URL
    if model_id.startswith("ollama:"):
        base_id = model_id.replace("ollama:", "")
        return OpenAIChatModel(base_id, provider=OllamaProvider(base_url=f"{config.ollama_host}/v1"))
    
    # Handle Bedrock specifically for the region
    if model_id.startswith("bedrock:"):
        base_id = model_id.replace("bedrock:", "")
        return BedrockConverseModel(base_id, provider=BedrockProvider(region_name=config.aws.region))
    
    return model_id


def create_agentic_sre(config: AgentSettings) -> Agent[None, ErrorDiagnosis]:
    """Create the Agentic SRE with all toolsets configured.

    Args:
        config: AgentSettings.

    Returns:
        Configured pydantic-ai Agent with structured output.
    """
    toolsets = [
        create_cloudwatch_toolset(config),
        create_github_mcp_toolset(config),
        create_slack_mcp_toolset(config),
    ]

    return Agent(
        _get_model(config),
        system_prompt=SYSTEM_PROMPT,
        output_type=ErrorDiagnosis,
        toolsets=toolsets,
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

    agent = create_agentic_sre(config)
    prompt = build_diagnosis_prompt(config, log_group, service_name, time_range_minutes)

    result = await agent.run(prompt)
    return result.output

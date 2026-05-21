"""Tests for the _get_model function in agent.py."""

import pytest
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock
from langchain_openai import ChatOpenAI

from atomic_sre.core.agent import _get_model, _infer_provider
from atomic_sre.core.settings import AgentSettings, AWSSettings, GitHubSettings, SlackSettings


class TestInferProvider:
    """Tests for _infer_provider helper."""

    def test_claude_routes_to_anthropic(self) -> None:
        """Claude models should route to the anthropic provider."""
        assert _infer_provider("claude-sonnet-4-5-20250929") == "anthropic"
        assert _infer_provider("claude-3-opus") == "anthropic"

    def test_gpt_routes_to_openai(self) -> None:
        """GPT models should route to the openai provider."""
        assert _infer_provider("gpt-4o") == "openai"
        assert _infer_provider("gpt-4o-mini") == "openai"

    def test_o_series_routes_to_openai(self) -> None:
        """O-series models should route to the openai provider."""
        assert _infer_provider("o1-preview") == "openai"
        assert _infer_provider("o3-mini") == "openai"

    def test_gemini_routes_to_google(self) -> None:
        """Gemini models should route to google-gla provider."""
        assert _infer_provider("gemini-2.0-flash") == "google-gla"

    def test_unknown_defaults_to_openai(self) -> None:
        """Unknown model names should default to openai."""
        assert _infer_provider("some-custom-model") == "openai"


class TestGetModel:
    """Tests for _get_model resolution."""

    @pytest.fixture
    def _base_settings(self) -> AgentSettings:
        """Create minimal AgentSettings for testing."""
        return AgentSettings(
            model="anthropic:claude-sonnet-4-5-20250929",
            anthropic_api_key="test-key",
            aws=AWSSettings(),
            github=GitHubSettings(
                personal_access_token="test",
                owner="test",
                repo="test",
                ref="main",
            ),
            slack=SlackSettings(channel_id="C123"),
        )

    def test_anthropic_returns_chat_anthropic(self, _base_settings: AgentSettings) -> None:
        """Anthropic provider should return ChatAnthropic."""
        _base_settings.model = "anthropic:claude-sonnet-4-5-20250929"
        _base_settings.anthropic_api_key = "test-key"
        model = _get_model(_base_settings)
        assert isinstance(model, ChatAnthropic)

    def test_openai_returns_chat_openai(self, _base_settings: AgentSettings) -> None:
        """OpenAI provider should return ChatOpenAI."""
        _base_settings.model = "openai:gpt-4o"
        _base_settings.openai_api_key = "test-key"
        model = _get_model(_base_settings)
        assert isinstance(model, ChatOpenAI)

    def test_ollama_returns_chat_openai_with_custom_base(self, _base_settings: AgentSettings) -> None:
        """Ollama provider should return ChatOpenAI with custom base_url."""
        _base_settings.model = "ollama:llama3"
        _base_settings.ollama_host = "http://custom-ollama:11434"
        model = _get_model(_base_settings)
        assert isinstance(model, ChatOpenAI)
        assert str(model.base_url) == "http://custom-ollama:11434/v1"

    def test_bedrock_returns_chat_bedrock(self, _base_settings: AgentSettings) -> None:
        """Bedrock provider should return ChatBedrock."""
        _base_settings.model = "bedrock:anthropic.claude-v2"
        model = _get_model(_base_settings)
        assert isinstance(model, ChatBedrock)

    def test_missing_api_key_raises_value_error(self, _base_settings: AgentSettings) -> None:
        """Missing API key should raise ValueError."""
        _base_settings.model = "anthropic:claude-sonnet-4-5-20250929"
        _base_settings.anthropic_api_key = None
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            _get_model(_base_settings)

    def test_bare_claude_auto_routes_to_anthropic(self, _base_settings: AgentSettings) -> None:
        """Bare claude model name should auto-route to anthropic."""
        _base_settings.model = "claude-sonnet-4-5-20250929"
        _base_settings.anthropic_api_key = "test-key"
        model = _get_model(_base_settings)
        assert isinstance(model, ChatAnthropic)

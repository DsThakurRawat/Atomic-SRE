"""Tests for diagnosis prompt rendering."""

from atomic_sre.core.prompts import build_diagnosis_prompt
from atomic_sre.core.settings import AgentSettings, AWSSettings, GitHubSettings, SlackSettings


class TestBuildDiagnosisPrompt:
    """Tests for build_diagnosis_prompt."""

    def test_prompt_contains_all_placeholders(self) -> None:
        """All template variables should be present in the rendered prompt."""
        config = AgentSettings(
            aws=AWSSettings(),
            github=GitHubSettings(
                personal_access_token="test",
                owner="my-org",
                repo="my-repo",
                ref="develop",
            ),
            slack=SlackSettings(channel_id="C999"),
        )

        prompt = build_diagnosis_prompt(
            config,
            log_group="/aws/logs/test",
            service_name="cartservice",
            time_range_minutes=15,
        )

        assert "/aws/logs/test" in prompt
        assert "cartservice" in prompt
        assert "15" in prompt
        assert "my-org" in prompt
        assert "my-repo" in prompt
        assert "develop" in prompt
        assert "C999" in prompt

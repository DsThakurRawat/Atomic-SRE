"""Tests for CloudWatch toolset creation."""

from unittest.mock import patch

from atomic_sre.core.settings import AgentSettings, AWSSettings, GitHubSettings, SlackSettings
from atomic_sre.core.tools import create_cloudwatch_toolset


class TestCreateCloudwatchToolset:
    """Tests for create_cloudwatch_toolset."""

    @patch("atomic_sre.core.tools.cloudwatch.boto3.client")
    def test_returns_list_with_search_error_logs(self, mock_boto_client) -> None:
        """Should return a list containing the search_error_logs tool."""
        config = AgentSettings(
            aws=AWSSettings(),
            github=GitHubSettings(
                personal_access_token="test",
                owner="test",
                repo="test",
                ref="main",
            ),
            slack=SlackSettings(channel_id="C123"),
        )
        toolset = create_cloudwatch_toolset(config)
        assert isinstance(toolset, list)
        assert len(toolset) == 1
        assert toolset[0].name == "search_error_logs"
